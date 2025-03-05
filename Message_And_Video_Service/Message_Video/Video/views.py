from django.shortcuts import render
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from datetime import datetime, timezone
from django.utils.timezone import now, timedelta
from .models import LiveSessionGroup, LiveSessionOneToOne,User
from .serializers import LiveSessionOneToOneSerializer, LiveSessionGroupSerializer
from Chat.jwt_decode import decode_jwt_token
from mongoengine.queryset.visitor import Q
# Create your views here.

class OneToOneLiveVideoViewSet(viewsets.ModelViewSet):
    queryset = LiveSessionOneToOne.objects.all()
    serializer_class = LiveSessionOneToOneSerializer
    
    def create(self, request, *args, **kwargs):
        """Tutor schedules a new session"""
        data = request.data
        tutor_id = data['caller']
        print(">>> :",data)
        if not all([data.get("receiver"), data.get("scheduled_at")]):
            return Response({"error": "Receiver and Scheduled time are required"}, status=400)
        session = data["session_code"]
        scheduled_at = datetime.strptime(data["scheduled_at"], "%Y-%m-%dT%H:%M:%SZ")
        
        min_time = datetime.now() + timedelta(minutes=5)
        max_time = datetime.now() + timedelta(hours=48)

        if not (min_time <= scheduled_at <= max_time):
            return Response({
                "error": "Sessions must be scheduled between 5 minutes and 48 hours from now."
            }, status=400)
        
        caller = User.objects(user_id=tutor_id).first()
        receiver = User.objects(user_id=data['receiver']).first()
        if not caller or not receiver:
            if not caller:
                caller = User(user_id=tutor_id)
                caller.save()
            if not receiver:
                receiver = User(user_id=data['receiver'])
                receiver.save()
                
        live_session = LiveSessionOneToOne(
            caller=caller,
            receiver=receiver,
            session_code=session,
            scheduled_at=scheduled_at,
            status="scheduled"
        )
        try:
            live_session.clean()
            live_session.validate()
            live_session.save()
        except ValidationError as e:
            return Response({"error": str(e)}, status=400)
        
        return Response({"message": "Session created successfully"}, status=201)
    
    def list(self, request, *args, **kwargs):
        """Tutor sees all their scheduled sessions"""
        tutor_data = decode_jwt_token(request)
        session = request.query_params.get('session_code', None)
        tutor_id = tutor_data['user_id']
        tutor = User.objects(user_id=tutor_id).first()
        if not tutor:
            return Response({"error": "Tutor not found"}, status=404)
        sessions = LiveSessionOneToOne.objects.filter(
            Q(caller=tutor) & Q(session_code=session) &
            (Q(status="scheduled") | Q(status="ongoing"))
            )
        
        return Response(LiveSessionOneToOneSerializer(sessions, many=True).data, status=200)
    
    
    @action(detail=True, methods=['post'])
    def start_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.start_call()
            return Response({'status': 'call started'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error one to one start_call:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.end_call()
            return Response({'status': 'call ended'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error one to one end_call:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
class LiveGroupVideoViewSet(viewsets.ModelViewSet):
    queryset = LiveSessionGroup.objects.all()
    serializer_class = LiveSessionGroupSerializer
    
    @action(detail=True, methods=['post'])
    def start_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.start_call()
            return Response({'status': 'call started'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error  start_call:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def end_call(self, request, pk=None):
        session = self.get_object()
        try:
            session.end_call()
            return Response({'status': 'call ended'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error  end_call:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def add_participant(self, request, pk=None):
        session = self.get_object()
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            session.add_participants(user)
            return Response({'status': 'participant added'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error  add_participant:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        
    @action(detail=True, methods=['post'])
    def remove_participant(self, request, pk=None):
        session = self.get_object()
        try:
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)
            session.remove_participant(user)
            return Response({'status': 'participant removed'}, status=status.HTTP_200_OK)
        except Exception as e:
            print("Error  remove_participant:" ,str(e))
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)