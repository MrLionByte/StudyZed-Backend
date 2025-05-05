from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.db import close_old_connections
from rest_framework.exceptions import AuthenticationFailed
from django.core.exceptions import PermissionDenied
from .authentication import JWTAuthentication
from django.utils.functional import SimpleLazyObject
from .user_management import get_or_create_user

class JWTForWebRTCMiddleware(BaseMiddleware):
    async def __call__(self, scope, receive=None, send=None):
        close_old_connections()
        query = scope.get("query_string", b"").decode("utf-8")
        query_parameters =  dict(qp.split("=") for qp in query.split("&"))
        token = query_parameters.get("token", None)
        if not token:
            await send({
                "type": "websocket.close",
                "code": 4000
            })
            return
        
        authentication = JWTAuthentication()
        try:
            user_data = await authentication.authenticate_websocket(token)
            if not user_data:
                await self.close_connection(send, 4001)
                return
            
            user = await get_or_create_user(user_data)
            if not user:
                await self.close_connection(self, send, 4002)
                return
            scope["user"] = user
            return await super().__call__(scope, receive, send)

        except (PermissionDenied, AuthenticationFailed):
            await send({
                "type": "websocket.close",
                "code": 4002
            })

        except Exception as e:
            await self.close_connection(send, 4004)
    
    async def close_connection(self, send, code, dummy=None):
        await send({
            "type": "websocket.close",
            "code": code
        })