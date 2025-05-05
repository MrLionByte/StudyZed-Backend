import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import OneToOneMessage, User
from .views import get_chatted_user
from .serializer import OneToOneMessageSerializer
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from django.utils.timezone import localtime
from channels.db import database_sync_to_async
from redis.asyncio import Redis
from .jwt_decode import decode_jwt_token_for_chat
from mongoengine.queryset.visitor import Q 
from django.conf import settings
import redis.asyncio as redis_async

logger = logging.getLogger(__name__)

class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = None
    
    async def get_redis(self):
        redis_host = "redis-service"
        redis_port = 6379
        redis_url = f"redis://{redis_host}:{redis_port}/2"
        self.redis = redis_async.from_url(
            redis_url,
            decode_responses=True,
            retry_on_timeout=True,
            socket_keepalive=True
        )
    
        return self.redis
    
    async def connect(self):
        if hasattr(self, 'is_connected') and self.is_connected:
            return
        self.is_connected = True
        
        try:
            self.user = self.scope['user']
            if not self.user or not hasattr(self.user, 'user_code'):
                await self.close()
                return
            recipient_user = self.scope['url_route']['kwargs']['user_code']
            
            if not User.objects(user_code=recipient_user).first():
                recipient = User(user_code=recipient_user)
                recipient.save()
                
            self.chat_id = recipient_user
            user_ids = sorted([self.user.user_code, recipient_user])
            
            self.room_group_name = f"chat_{user_ids[0]}_{user_ids[1]}"
            self.room_group_name = self.room_group_name.replace("-", "_")
            
            redis = await self.get_redis()
            channel_key = f"channel:{self.channel_name}"
            group_key = f"group:{self.room_group_name}"
            
            is_member = await redis.sismember(group_key, self.channel_name)
            if not is_member:
                await redis.sadd(group_key, self.channel_name)
                
                await redis.hset(channel_key, mapping={
                    'user': self.user.user_code,
                    'group': self.room_group_name,
                    'connected_at': datetime.now().isoformat()
                })
                
                await redis.expire(channel_key, 86400)

                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            else:
                logger.info(f"Already connected to group: {self.room_group_name}")
            
            await self.accept()
            
            # if not hasattr(self, "channel_added") or not self.channel_added:
            #     await self.channel_layer.group_add(
            #         self.room_group_name,
            #         self.channel_name
            #     )
            #     self.channel_added = True 
            
            # await self.accept()
    
            history = await self.get_chat_history(self.user.user_code, recipient_user)
            
            if history:
                await self.send(text_data=json.dumps({
                    'type': 'chat_history',
                    'messages': history
                }, default=str))
        except Exception as e:
            logger.error(f"Connection error in connect: {str(e)}")

    async def disconnect(self, close_code):
        redis = await self.get_redis()
        group_key = f"group:{self.room_group_name}"
        channel_key = f"channel:{self.channel_name}"
        
        await redis.srem(group_key, self.channel_name)

        await redis.delete(channel_key)
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            # message_type = data.get('type')
            message = data.get("message")
            sender = data.get('sender')
            recipient = data.get('chat_id')
            
            if not all([message, sender, recipient]):
                return
            iso_timestamp = datetime.now().isoformat()
            saved_message = await self.save_message(
                sender, recipient, message, iso_timestamp)
            
            if not saved_message:
                return
                
            # Broadcast message to room group
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'chat_id': recipient,
                    'timestamp': iso_timestamp,
                }
            )
        except Exception as e:
            logger.error(f"Error in receive: {str(e)}")
            # await self.send(text_data=json.dumps({
            #     'error': str(e)
            # }))
            
            
    async def chat_message(self, event):
        if hasattr(self, 'message_handled') and self.message_handled == event['timestamp']:
            return
        self.message_handled = event['timestamp']
        await self.send(text_data=json.dumps({
                'type': event['type'], 
                'message': event['message'],
                'sender': event['sender'],
                'chat_id': event['chat_id'],
                'timestamp': event['timestamp']
            }))

    @database_sync_to_async
    def save_message(
        self, sender_id, recipient_id, content, messaged_time
                        ):
        sender = User.objects(user_code=sender_id).first()
        recipient = User.objects(user_code=recipient_id).first()
            
        if not sender or not recipient:
            return None
        
        message = OneToOneMessage(
                sender=sender,
                recipient=recipient,
                content=content,
                created_on=messaged_time
            )
        message.save()
        return message
        
    @database_sync_to_async
    def get_chat_history(self, user_code, recipient_code):
        try:
            user = User.objects(user_code=user_code).first()
            recipient = User.objects(user_code=recipient_code).first()
            
            if not user or not recipient:
                return []
            messages = OneToOneMessage.objects(
                    (Q(sender=user) & Q(recipient=recipient)) |
                    (Q(sender=recipient) & Q(recipient=user))
                ).order_by('timestamp')
            
            return [{
                'message': msg.content,
                'sender': msg.sender.user_code,
                'timestamp': msg.created_on
                } for msg in messages]
        except Exception as e:
            logger.error(f"Error fetching chat history: {str(e)}")
            return []

class PersonalChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            self.user = self.scope["user"]
            if not self.user or not hasattr(self.user, 'user_id'):
                await self.close()
                return
            recipient_user = self.scope['url_route']['kwargs']['id']
            
            user_ids = sorted([int(self.user.user_id), int(recipient_user)])
            self.room_group_name = f"chat_{user_ids[0]}_{user_ids[1]}"
            await self.channel_layer.group_add(
                self.room_group_name,
                self.channel_name
            )
            await self.accept()
            
        except Exception as e:
            logger.error(f"Connection error in PersonalChatConsumer: {str(e)}")

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data['message']
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message
            }
        )
    
    async def disconnect(self, code):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def chat_message(self, event):
        message = event['message']
        await self.send(text_data=json.dumps({
            "message": message
        }))
        
    

class OnlineStatusConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_group_name = 'user_group'
        
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
    
    async def disconnect(self, message):
        self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        
#   
        