import socketio
from django.conf import settings

sio = socketio.Server()

@sio.event
def connect (sid, environ):
    print("Client connected", sid)
    
@sio.event
def disconnect(sid):
    print('Client disconnected:', sid)
    

if __name__ == '__main__':
    import eventlet
    import eventlet.wsgi
    from Message_Video.asgi import application

    app = socketio.WSGIApp(sio, application)
    eventlet.wsgi.server(eventlet.listen(('', 8000)), app)
