from django.shortcuts import render
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from .models import (User ,OneToOneMessage, 
                     OpenChatRoom, OpenChatMessage)
from mongoengine.queryset.visitor import Q
from .serializer import OneToOneMessageSerializer
from .jwt_decode import decode_jwt_token
from datetime import datetime

# Create your views here.

@api_view(['GET'])
def get_chatted_user(request, user_code):
    print("WORKING WELL                 >>>>>>>>>>>", user_code)
    current_user = User.objects(user_code=user_code).first()
    if current_user:
        print(current_user)
    else:
    # current_user = User.objects.get(user_code=user_code).exist()
    
    # if not current_user:
        user_decoded_data = decode_jwt_token(request)
        print("DECODED :",user_decoded_data)
        current_user = User.objects.create(
            user_id = str(user_decoded_data.get("user_id")),
            user_code=user_decoded_data.get("user_code"),
            user_role=user_decoded_data.get("user_role"),
            email = user_decoded_data.get("user_email"),
            )

    try:
        messages = OneToOneMessage.objects(
            Q(sender=current_user.id) | 
            Q(recipient=current_user.id)
        )

        chatted_user_ids = set()
        for message in messages:
            if message.sender and str(message.sender.id) != str(current_user.id):
                chatted_user_ids.add(message.sender.id)
            if message.recipient and str(message.recipient.id) != str(current_user.id):
                chatted_user_ids.add(message.recipient.id)

        
        chatted_users = User.objects(
            id__in=list(chatted_user_ids)
        ).only('user_code', 'user_role', 'email')

        
        response_data = []
        for user in chatted_users:
            
            latest_message = OneToOneMessage.objects(
                (Q(sender=current_user.id) & Q(recipient=user.id)) |
                (Q(sender=user.id) & Q(recipient=current_user.id))
            ).order_by('-timestamp').first()

            response_data.append({
                "user_code": user.user_code,
                "role": user.user_role,
                "email": user.email,
                "latest_message": {
                    "content": latest_message.content if latest_message else None,
                    "timestamp": latest_message.timestamp if latest_message else None,
                    "is_sender": str(latest_message.sender.id) == str(current_user.id) if latest_message else None
                } if latest_message else None
            })

        response_data.sort(
            key=lambda x: (x['latest_message'] or {}).get('timestamp', datetime.min), 
            reverse=True
        )

        return Response({
            "chatted_users": response_data
        }, status=status.HTTP_200_OK)
        
    except User.DoesNotExist:
        print("Error user not exsist")
        return Response(
            {'error': 'User not found'},
            status=status.HTTP_404_NOT_FOUND
        )
        
    except Exception as e:
        print("ERROROROROR ::", e)
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
def get_chat_history(request, user_code, selected_user_code):
    """
    Get chat history between two users
    """
    try:
        current_user = User.objects.get(user_code=user_code)
        selected_user = User.objects.get(user_code=selected_user_code)
        
        messages = OneToOneMessage.objects.filter(
            (Q(sender=current_user) & Q(recipient=selected_user)) |
            (Q(sender=selected_user) & Q(recipient=current_user))
        ).order_by('timestamp')

        serializer = OneToOneMessageSerializer(messages, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)
    
    except User.DoesNotExist:
        return Response(
            {'error': 'One or both users not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
        
    