from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, HTTPException
from auth import get_current_user_by_token
from database import SessionDepend, User
import json
from utils import save_group_message, save_private_message

class ConnectionInfo:
    def __init__(self, user: User, group_id: int = None, friend_id: int = None):
        self.user = user
        self.group_id = group_id
        self.friend_id = friend_id
        
class WsInfo:
    def __init__(self, websocket: WebSocket, info: ConnectionInfo):
        self.websocket = websocket
        self.info = info

class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def authenticate(self, websocket: WebSocket, session: SessionDepend, data: json):
        try:
            user = get_current_user_by_token(data.get("token"), session)
            info = ConnectionInfo(user, data.get("group_id"), data.get("friend_id"))
            wsinfo = WsInfo(websocket, info)
            if not any(websocket in active_ws for active_ws in self.active_connections):
                await websocket.send_text("authenticated")
                self.active_connections.append(wsinfo)
            else:
                await websocket.send_text("already authenticated")
            return wsinfo
        except:
            return False
          
    def disconnect(self, wsinfo: WsInfo):
        if wsinfo in self.active_connections:
            self.active_connections.remove(wsinfo)
        
    async def group_broadcast(self, group_id: int, message: str):
        for connection in self.active_connections:
            if connection.info.group_id == group_id:
                await connection.websocket.send_text(message)
            
    async def private_broadcast(self, user_id: int, friend_id: int, message: json):
        for connection in self.active_connections:
            if connection.info.friend_id == user_id and connection.info.user.id == friend_id:
                await connection.websocket.send_text(message)
                
    async def handle_message(self, session: SessionDepend, wsinfo: WsInfo, message: dict):
        try:
            if(message.get("type") == "group_message"):
                save_group_message(wsinfo.info.user, message.get("group_id"), message.get("message"), session)
                await wsinfo.websocket.send_text("group message sent")
                await self.group_broadcast(message.get("group_id"), message.get("message"))
            elif(message.get("type") == "private_message"):
                save_private_message(wsinfo.info.user, message.get("friend_id"), message.get("message"), session)
                await wsinfo.websocket.send_text("private message sent")
                await self.private_broadcast(wsinfo.info.user.id, message.get("friend_id"), message.get("message"))
            else:
                await wsinfo.websocket.send_text("invalid message type")
                await wsinfo.websocket.close(code=4003)
                raise WebSocketDisconnect
        except WebSocketDisconnect as e:
            raise e
        except HTTPException as e:
            await wsinfo.websocket.send_text(str(e))
            await wsinfo.websocket.close(code=4003)
            raise WebSocketDisconnect

manager = ConnectionManager()
wsrouter = APIRouter()

@wsrouter.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, session: SessionDepend):
    await websocket.accept()
    wsinfo = None
    try:
        while True:
            raw_data = await websocket.receive_text()
            data = json.loads(raw_data)
            if data.get("type") == "auth_request":
                wsinfo = await manager.authenticate(websocket, session, data)
                if not wsinfo:
                    await websocket.send_text("authentication failed")
                    await websocket.close(code=4003)
                    break
            elif not wsinfo:
                await websocket.send_text("not authenticated")
                await websocket.close(code=4003)
                raise WebSocketDisconnect
            else:
                await manager.handle_message(session, wsinfo, data)
    except WebSocketDisconnect:
        manager.disconnect(wsinfo)
