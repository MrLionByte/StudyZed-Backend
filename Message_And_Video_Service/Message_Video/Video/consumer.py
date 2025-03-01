import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import OneToOneMessage, User
from .views import get_chatted_user
from .serializer import OneToOneMessageSerializer
from asgiref.sync import sync_to_async
from datetime import datetime, timezone
from channels.db import database_sync_to_async

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         try:
            
#             query_string = self.scope['query_string'].decode()
#             query_params = dict(q.split('=') for q in query_string.split('&') if q)
#             user_id = query_params.get('user_id')
            
#             if not user_id:
#                 print("No user_id provided")
#                 await self.close()
#                 return
            
#             chat_with_user = self.scope['url_route']['kwargs']['chat_id']
#             user_ids = [str(user_id), str(chat_with_user)] 
#             user_ids = sorted(user_ids)
            
            
#             self.private_chat_room = f"chat_{user_ids[0]}--{user_ids[1]}"
#             self.user_id = user_id 
            
#             # Notify both users about the new conversation
#             await self.channel_layer.group_add(
#                 self.private_chat_room,
#                 self.channel_name
#             )
            
#             #  Add user to personal notfy channel
#             await self.channel_layer.group_add(
#                 f"user_{user_id}",
#                 self.channel_name
#             )

#             await self.channel_layer.group_add(
#                 self.private_chat_room,
#                 self.channel_name
#             )

#             await self.accept()

#         except Exception as e:
#             print(f"Connection failed: {str(e)}")
#             await self.close()

#     @sync_to_async
#     def save_message(self, sender_id, recipient_id, content):
#         print("SENDER ID TESTING", sender_id, recipient_id, content)
#         try:
#             sender = User.objects(user_id=sender_id).first()
#             if not sender:
#                 print(f"Sender with ID {sender_id} not found")
#                 return None
                
#             # Get or create recipient
#             recipient = User.objects(user_id=recipient_id).first()
#             if not recipient:
#                 print(f"Recipient with ID {recipient_id} not found")
#                 return None
            
#             message = OneToOneMessage(
#                 sender = sender,
#                 recipient = recipient,
#                 content = content
#             )
#             message.save()
#             return message
        
#         except Exception as e:
#             print(f"Error in receive: {str(e)}")
#             return None


#     async def receive(self, text_data=None, bytes_data=None):
#         try:
#             data = json.loads(text_data)
#             message_content = data['message']
#             recipient_id = self.scope['url_route']['kwargs']['chat_id']
#             sender_id = self.user_id  # Use the stored user_id

#             # Save the message to the database
#             message = await self.save_message(sender_id, recipient_id, message_content)
            
#             if message:
#                 # Send the message to the private chat
#                 await self.channel_layer.group_send(
#                     self.private_chat_room,
#                     {
#                         'type': 'chat_message',
#                         'message': message_content,
#                         'sender_id': sender_id,
#                         'timestamp': message.timestamp.isoformat()
#                     }
#                 )
#         except Exception as e:
#             print(f"Error in receive: {str(e)}")

#     async def disconnect(self, code):
#         try:
#             await self.channel_layer.group_discard(
#                 self.private_chat_room,
#                 self.channel_name
#             )
#             # Also remove from personal notification channel
#             if hasattr(self, 'user_id'):
#                 await self.channel_layer.group_discard(
#                     f"user_{self.user_id}",
#                     self.channel_name
#                 )
#         except Exception as e:
#             print(f"Error in disconnect: {str(e)}")

#     async def chat_message(self, event):
#         try:
#             await self.send(text_data=json.dumps({
#                 'message': event['message'],
#                 'sender_id': event['sender_id'],
#                 'timestamp': event['timestamp']
#             }))
#         except Exception as e:
#             print(f"Error in chat_message: {str(e)}")

# class ChatConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         self.userID = self.scope["url_route"]["kwargs"]["userID"]
#         self.room_group_name = f"chat_{self.userID}"
#         query_string = self.scope['query_string'].decode()
#         query_params = dict(qc.split("=") for qc in query_string.split("&") if "=" in qc)
#         self.tutor_code = query_params.get("user_id", None)
                
#         print(f"Connecting to room group: {self.room_group_name}")
#         await self.channel_layer.group_add(
#             self.room_group_name,
#             self.channel_name
#         )
#         await self.accept()
#         print(f'WebSocket connected : {self.channel_name}')
    
#     async def disconnect(self, close_code):
#         print(f"WebSocket disconnecting : {self.channel_name}, close_code : {close_code}")
        
#         await self.channel_layer.group_discard(
#             self.room_group_name,
#             self.channel_name
#         )        
#         print(f"WebSocket disconnected : {self.channel_name}")
        
#     async def receive(self, text_data=None, bytes_data=None):
#         print("Received Here ^-^")
#         print(text_data)
#         text_data_json = json.loads(text_data)
#         message = text_data_json["message"]
#         recipient_id = text_data_json['recipient_id']
#         sender_id = text_data_json['sender_id']
#         await self.save_message(sender_id, recipient_id, message)
        
#         # To senders feed or room
#         await self.channel_layer.group_send(
#             f"chat_{sender_id}",
#             {
#                 "type"      :   "chat_message",
#                 "message"   :   message,
#                 "sender_id" :   sender_id,
#                 "recipient_id": recipient_id,
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
#         )
        
#         # To recipient feed or room
#         await self.channel_layer.group_send(
#             f"chat_{recipient_id}",
#             {
#                 "type"      :   "chat_message",
#                 "message"   :   message,
#                 "sender_id" :   sender_id,
#                 "recipient_id": recipient_id,
#                 "timestamp": datetime.now(timezone.utc).isoformat()
#             }
#         )
        
#     async def chat_message(self, event):
        
#         await self.send(text_data=json.dumps(event))
    
#     @database_sync_to_async
#     def save_message(self, sender_id, recipient_id, content):
#         sender = User.objects(user_id=sender_id).first()
#         recipient = User.objects(user_id=recipient_id).first()
#         OneToOneMessage(
#             sender = sender,
#             recipient = recipient,
#             content = content
#         ).save()
        

# consumers.py
import json
import redis
from redis.asyncio import Redis
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from datetime import datetime, timezone
from .models import User, OneToOneMessage
from .jwt_decode import decode_jwt_token_for_chat
from mongoengine.queryset.visitor import Q 



class ChatConsumer(AsyncWebsocketConsumer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.redis = None
    
    async def get_redis(self):
        if not self.redis:
            self.redis = Redis(
                host='redis_service_2', 
                port=6379,              
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
                    'connected_at': datetime.now(timezone.utc).isoformat()
                })
                
                await redis.expire(channel_key, 86400)

                await self.channel_layer.group_add(
                    self.room_group_name,
                    self.channel_name
                )
            else:
                print(f"Channel {self.channel_name} is already a member of {group_key}")
            
            await self.accept()
            
            # if not hasattr(self, "channel_added") or not self.channel_added:
            #     await self.channel_layer.group_add(
            #         self.room_group_name,
            #         self.channel_name
            #     )
            #     self.channel_added = True 
            
            # print("Connection accepted successfully DONE")
            # await self.accept()
    
            history = await self.get_chat_history(self.user.user_code, recipient_user)
            
            if history:
                await self.send(text_data=json.dumps({
                    'type': 'chat_history',
                    'messages': history
                }))
        except Exception as e:
            print(f"Connection error in connect : {str(e)}")

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
            
            saved_message = await self.save_message(sender, recipient, message)
            
            if not saved_message:
                return
                
            # Broadcast message to room group
            iso_timestamp = datetime.now(timezone.utc).isoformat()
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'sender': sender,
                    'chat_id': recipient,
                    'date': iso_timestamp.split("T")[0],
                    'time': iso_timestamp.split("T")[1].split("Z")[0],
                }
            )
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            
            
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
    def save_message(self, sender_id, recipient_id, content):
        sender = User.objects(user_code=sender_id).first()
        recipient = User.objects(user_code=recipient_id).first()
            
        if not sender or not recipient:
            return None
        
        message = OneToOneMessage(
                sender=sender,
                recipient=recipient,
                content=content
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
                'date': msg.date.isoformat(),
                'time': msg.time.isoformat()[:5]
            } for msg in messages]
        except Exception as e:
            print("ERROR AT GET CHAt history", e)

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
            print(f"Connection error: {str(e)}")

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
        
        