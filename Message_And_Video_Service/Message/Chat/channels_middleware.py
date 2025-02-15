from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.db import close_old_connections
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import PermissionDenied
from .authentication import JWTAuthentication
from django.utils.functional import SimpleLazyObject
from .user_management import get_or_create_user

class JWTForWebsocketMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive=None, send=None):
        close_old_connections()
        print("CHANNEl MIDDLE WARE :",scope, receive, send)
        query = scope.get("query_string", b"").decode("utf-8")
        query_parameters =  dict(qp.split("=") for qp in query.split("&"))
        token = query_parameters.get("token", None)
        
        print("CHANNEl MIDDLE WARE Token DONE :",token)
        if not token:
            await send({
                "type": "websocket.close",
                "code": 4000
            })
            return
        
        authentication = JWTAuthentication()
        try:
            user_data = await authentication.authenticate_websocket(token)
            print("CHANNEL MIDDLEWARE 22 ", user_data)
            if not user_data:
                await self.close_connection(send, 4001)
                return
            
            user = await get_or_create_user(user_data)
            if not user:
                await self.close_connection(self, send, 4002)
                return
            print("Channel Middleware 33", user)
            # scope["user"] = SimpleLazyObject(lambda: user)
            scope["user"] = user
            print("Channel Middleware 44", scope,">>", receive,">>", send)
            return await super().__call__(scope, receive, send)

        except (PermissionDenied, AuthenticationFailed):
            print("ERROR in JWT MIDDLEWARE")
            await send({
                "type": "websocket.close",
                "code": 4002
            })

        except Exception as e:
            print("ERROR as Exception :", e)
            await self.close_connection(send, 4004)
    
    async def close_connection(self, send, code, dummy=None):
        await send({
            "type": "websocket.close",
            "code": code
        })