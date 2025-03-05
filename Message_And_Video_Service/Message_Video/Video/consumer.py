import json
import redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone
from .models import LiveSessionGroup, User, OpenChatRoom

redis_client = redis.StrictRedis(host='redis_service_2', port=6379, db=3, decode_responses=True)


class VideoCallConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'video_call_{self.room_id}'
        
       
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
       
        await self.accept()
        
        
        user = self.scope['user']
        
        if not user.is_anonymous:
           
            await self.add_participant_to_session(user)
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_joined',
                    'user_id': str(user.id),
                    'user_code': user.code,
                    'message': f"{user.code} joined the call"
                }
            )
    
    async def disconnect(self, close_code):
        user = self.scope['user']
        if not user.is_anonymous:
            
            await self.remove_participant_from_session(user)
            
           
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'user_left',
                    'user_id': str(user.id),
                    'message': f"{user.code} left the call"
                }
            )
        
        
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        print("data :", data)
      
        if message_type == 'join':
           
            print(f"User {data.get('user_code')} joined with role {data.get('role')}")
            return
        
        elif message_type == 'offer':
           
            recipient_id = data.get('recipient_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_offer',
                    'offer': data.get('offer'),
                    'sender_id': str(self.scope['user'].id),
                    'recipient_id': recipient_id
                }
            )
        
        elif message_type == 'answer':
           
            recipient_id = data.get('recipient_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'webrtc_answer',
                    'answer': data.get('answer'),
                    'sender_id': str(self.scope['user'].id),
                    'recipient_id': recipient_id
                }
            )
        
        elif message_type == 'ice_candidate':
            
            recipient_id = data.get('recipient_id')
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'ice_candidate',
                    'ice': data.get('ice'),
                    'sender_id': str(self.scope['user'].id),
                    'recipient_id': recipient_id
                }
            )
        
        elif message_type == 'start_call':
           
            user = self.scope['user']
            is_host = await self.check_if_host(user)
            
            if is_host:
                await self.start_session()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_started',
                        'message': 'The video call has started'
                    }
                )
        
        elif message_type == 'end_call':
            
            user = self.scope['user']
            is_host = await self.check_if_host(user)
            
            if is_host:
                await self.end_session()
                await self.channel_layer.group_send(
                    self.room_group_name,
                    {
                        'type': 'call_ended',
                        'message': 'The video call has ended'
                    }
                )
                
        elif message_type == 'chat_message':
            
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': data.get('message'),
                    'sender_id': str(self.scope['user'].id),
                    'sender_name': data.get('sender_name', self.scope['user'].code)
                }
            )
    
   
    async def webrtc_offer(self, event):
       
        if str(self.scope['user'].id) == event.get('recipient_id'):
            await self.send(text_data=json.dumps({
                'type': 'offer',
                'offer': event['offer'],
                'sender_id': event['sender_id']
            }))
    
    async def webrtc_answer(self, event):
        
        if str(self.scope['user'].id) == event.get('recipient_id'):
            await self.send(text_data=json.dumps({
                'type': 'answer',
                'answer': event['answer'],
                'sender_id': event['sender_id']
            }))
    
    async def ice_candidate(self, event):
        
        if str(self.scope['user'].id) == event.get('recipient_id'):
            await self.send(text_data=json.dumps({
                'type': 'ice_candidate',
                'ice': event['ice'],
                'sender_id': event['sender_id']
            }))
    
    async def user_joined(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'user_id': event['user_id'],
            'user_code': event['user_code'],
            'message': event['message']
        }))
    
    async def user_left(self, event):
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'user_id': event['user_id'],
            'message': event['message']
        }))
    
    async def call_started(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_started',
            'message': event['message']
        }))
    
    async def call_ended(self, event):
        await self.send(text_data=json.dumps({
            'type': 'call_ended',
            'message': event['message']
        }))
        
    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name']
        }))
    
   
    @database_sync_to_async
    def add_participant_to_session(self, user):
        try:
            session = LiveSessionGroup.objects.get(session=self.room_id)
           
            if session.status == "ended":
                session.status = "live"
                session.ended_at = None
                session.save()
            session.add_participants(user)
            return True
        except LiveSessionGroup.DoesNotExist:
            session = LiveSessionGroup(
                session=self.room_id,
                host=user,
                status='live'
            )
            session.save()
            session.add_participants(user)
            return True
    
    @database_sync_to_async
    def remove_participant_from_session(self, user):
        try:
            session = LiveSessionGroup.objects.get(
                session=self.room_id)
            session.remove_participant(user)
            
            if len(session.participants) == 0:
                session.end_call()
            return True
        except LiveSessionGroup.DoesNotExist:
            return False
    
    @database_sync_to_async
    def check_if_host(self, user):
        try:
            session = LiveSessionGroup.objects.get(
                session=self.room_id)
            return session.host == user
        except LiveSessionGroup.DoesNotExist:
            return False
    
    @database_sync_to_async
    def start_session(self):
        try:
            session = LiveSessionGroup.objects.get(
                session=self.room_id)
            session.start_call()
            return True
        except LiveSessionGroup.DoesNotExist:
            return False
    
    @database_sync_to_async
    def end_session(self):
        try:
            session = LiveSessionGroup.objects.get(
                session=self.room_id)
            session.end_call()
            return True
        except LiveSessionGroup.DoesNotExist:
            return False
        
class LiveSessionOneToOneConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.user = self.scope['user']
        self.receiver_id = self.scope['url_route']['kwargs']['receiver']
        user_ids = sorted([str(self.user.user_code), str(self.receiver_id)])
        self.room_group_name = f'video_call_{"_".join(user_ids)}'
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        data = json.loads(text_data)
        message_type = data.get('type')
        print("----------", data, message_type)
        if message_type in ['offer', 'answer', 'ice_candidate']:
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'webrtc_message',
                'message_type': message_type,
                message_type: data[message_type],
                'sender_id': str(self.user.user_id)
            })
        elif message_type == 'end_call':
            await self.channel_layer.group_send(self.room_group_name, {
                'type': 'call_ended'
            })
    
    async def webrtc_message(self, event):
        """ Handles WebRTC messages like offer, answer, and ice_candidate """
        await self.send(text_data=json.dumps({
            "type": event["message_type"],  
            event["message_type"]: event[event["message_type"]], 
            "sender_id": event["sender_id"],
        }))

    async def call_ended(self, event):
        await self.send(text_data=json.dumps({'type': 'call_ended'}))