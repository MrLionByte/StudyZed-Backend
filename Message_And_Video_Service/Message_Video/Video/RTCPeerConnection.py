from aiortc import RTCPeerConnection, RTCSessionDescription
import json


pcs = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    
    pc = RTCPeerConnection()
    pcs.add(pc)
    
    @pc.on('datachannel')
    def on_dataChannel(channel):
        @channel.on("message")
        async def on_message(message):
            pass
    
    async for msg in ws:
        if msg.type == web.WSMsgType.TEXT:
            data = json.loads(msg.data)

            if data["type"] == "offer":
                await pc.setRemoteDescription(RTCSessionDescription(
                    sdp=data["sdp"], type=data["type"]))
                answer = await pc.createAnswer()
                await pc.setLocalDescription(answer)
                await ws.send_json({
                    "type": pc.localDescription.type,
                    "sdp": pc.localDescription.sdp
                })

            elif data["type"] == "candidate":
                candidate = data["candidate"]
                await pc.addIceCandidate(candidate)
                
        elif msg.type == web.WSMsgType.ERROR:
            print(f'WebSocket connection closed with exception {ws.exception()}')

    pcs.discard(pc)
    return ws

