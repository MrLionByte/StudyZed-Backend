from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async
from django.db import close_old_connections
from django.core.exceptions import PermissionDenied
from .authentication import JWTAuthentication


class JWTForWebsocketMiddleware():
    async def __call__(self, scope, receive, send):
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
            user = await authentication.authenticate_websocket(token)
            if user:
                scope["user"] = user
            else:
                await send({
                    "type": "websocket.close",
                    "code": 4000
                })
                return
            
            return await super().__call__(scope, receive, send)

        except PermissionDenied:
            await send({
                "type": "websocket.close",
                "code": 4002
            })
        
