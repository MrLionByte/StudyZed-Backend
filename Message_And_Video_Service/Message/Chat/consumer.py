import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import OneToOneMessage, User

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        try:
            
            query_string = self.scope['query_string'].decode()
            query_params = dict(q.split('=') for q in query_string.split('&') if q)
            user_id = query_params.get('user_id')
            
            if not user_id:
                print("No user_id provided")
                await self.close()
                return
            
            chat_with_user = self.scope['url_route']['kwargs']['chat_id']
            user_ids = [str(user_id), str(chat_with_user)] 
            user_ids = sorted(user_ids)
            
            
            self.private_chat_room = f"chat_{user_ids[0]}--{user_ids[1]}"
            self.user_id = user_id 
            
            # Notify both users about the new conversation
            await self.channel_layer.group_add(
                self.private_chat_room,
                self.channel_name
            )
            
            #  Add user to personal notfy channel
            await self.channel_layer.group_add(
                f"user_{user_id}",
                self.channel_name
            )

            await self.channel_layer.group_add(
                self.private_chat_room,
                self.channel_name
            )

            await self.accept()

        except Exception as e:
            print(f"Connection failed: {str(e)}")
            await self.close()

    @sync_to_async
    def save_message(self, sender_id, recipient_id, content):
        print("SENDER ID TESTING", sender_id, recipient_id, content)
        try:
            sender = User.objects(user_id=sender_id).first()
            if not sender:
                print(f"Sender with ID {sender_id} not found")
                return None
                
            # Get or create recipient
            recipient = User.objects(user_id=recipient_id).first()
            if not recipient:
                print(f"Recipient with ID {recipient_id} not found")
                return None
            
            message = OneToOneMessage(
                sender = sender,
                recipient = recipient,
                content = content
            )
            message.save()
            return message
        
        except Exception as e:
            print(f"Error in receive: {str(e)}")
            return None


    async def receive(self, text_data=None, bytes_data=None):
        try:
            data = json.loads(text_data)
            message_content = data['message']
            recipient_id = self.scope['url_route']['kwargs']['chat_id']
            sender_id = self.user_id  # Use the stored user_id

            # Save the message to the database
            message = await self.save_message(sender_id, recipient_id, message_content)
            
            if message:
                # Send the message to the private chat
                await self.channel_layer.group_send(
                    self.private_chat_room,
                    {
                        'type': 'chat_message',
                        'message': message_content,
                        'sender_id': sender_id,
                        'timestamp': message.timestamp.isoformat()
                    }
                )
        except Exception as e:
            print(f"Error in receive: {str(e)}")

    async def disconnect(self, code):
        try:
            await self.channel_layer.group_discard(
                self.private_chat_room,
                self.channel_name
            )
            # Also remove from personal notification channel
            if hasattr(self, 'user_id'):
                await self.channel_layer.group_discard(
                    f"user_{self.user_id}",
                    self.channel_name
                )
        except Exception as e:
            print(f"Error in disconnect: {str(e)}")

    async def chat_message(self, event):
        try:
            await self.send(text_data=json.dumps({
                'message': event['message'],
                'sender_id': event['sender_id'],
                'timestamp': event['timestamp']
            }))
        except Exception as e:
            print(f"Error in chat_message: {str(e)}")