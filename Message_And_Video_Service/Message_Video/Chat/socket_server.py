import socketio
import logging
from django.conf import settings

logger = logging.getLogger(__name__)
sio = socketio.Server()

@sio.event
def connect (sid, environ):
    logger.info("Client connected @Socket Server :", sid)
    
@sio.event
def disconnect(sid):
    logger.info('Client disconnected @Socket Server:', sid)
    

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    from Message_Video.asgi import application

    app = socketio.WSGIApp(sio, application)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
