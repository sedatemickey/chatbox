from fastapi import WebSocket, APIRouter, WebSocketDisconnect, Depends, HTTPException
from auth import get_current_user_by_token
from database import SessionDepend, User
import json
from utils import save_group_message, save_private_message, get_message_by_groupid, get_message_by_userid, get_aichat_message, save_aichat_message, clear_aichat_message
from aichat import chat

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
            if not any(wsinfo == active_ws for active_ws in self.active_connections):
                sendJson = {"type": "info", "message": "authenticated"}
                await websocket.send_text(json.dumps(sendJson))
                self.active_connections.append(wsinfo)
            else:
                sendJson = {"type": "info", "message": "already authenticated"}
                await websocket.send_text(json.dumps(sendJson))
            return wsinfo
        except Exception as e:
            print(e)
            return False
          
    def disconnect(self, wsinfo: WsInfo):
        if wsinfo in self.active_connections:
            self.active_connections.remove(wsinfo)
        
    async def group_broadcast(self, group_id: int, message: str, user_id: int | None = None):
        for connection in self.active_connections:
            if connection.info.group_id == group_id and connection.info.user.id != user_id:
                sendJson = {"type": "get_message", "message": message}
                await connection.websocket.send_text(json.dumps(sendJson))
            
    async def private_broadcast(self, user_id: int, friend_id: int, message: json):
        for connection in self.active_connections:
            if connection.info.friend_id == user_id and connection.info.user.id == friend_id:
                sendJson = {"type": "get_message", "message": message}
                await connection.websocket.send_text(json.dumps(sendJson))
                
    async def handle_message(self, session: SessionDepend, wsinfo: WsInfo, message: dict):
        try:
            # 发送群组信息
            if(message.get("type") == "group_message"):
                save_group_message(wsinfo.info.user, message.get("group_id"), message.get("message"), session)
                sendJson = {"type": "info", "message": "group message sent"}
                await wsinfo.websocket.send_text(json.dumps(sendJson))
                await self.group_broadcast(message.get("group_id"), message.get("message"), wsinfo.info.user.id)
                
            # 发送私聊信息
            elif(message.get("type") == "private_message"):
                save_private_message(wsinfo.info.user, message.get("friend_id"), message.get("message"), session)
                sendJson = {"type": "info", "message": "private message sent"}
                await wsinfo.websocket.send_text(json.dumps(sendJson))
                await self.private_broadcast(wsinfo.info.user.id, message.get("friend_id"), message.get("message"))
            
            # 发送Aichat信息
            # 已移动到aichat.py
            
            elif(message.get("type") == "clear_aichat_message"):
                clear_aichat_message(wsinfo.info.user, session)
                sendJson = {"type": "aichat_messages", "aichat_messages": get_aichat_message(wsinfo.info.user, session), "message": "chat changed"}
                await wsinfo.websocket.send_text(json.dumps(sendJson))
                
                
            # 获取新chat的历史消息
            elif(message.get("type") == "change_chat"):
                wsinfo.info.group_id = message.get("group_id")
                wsinfo.info.friend_id = message.get("friend_id")
                if wsinfo.info.group_id:
                    # 是群组
                    sendJson = {"type": "group_messages", "group_messages": get_message_by_groupid(wsinfo.info.user, wsinfo.info.group_id, session), "message": "chat changed"}
                elif wsinfo.info.friend_id:
                    # 是私聊
                    sendJson = {"type": "friends_messages", "friends_messages": get_message_by_userid(wsinfo.info.friend_id, wsinfo.info.user, session), "message": "chat changed"}
                else:
                    # 是Aichat
                    sendJson = {"type": "aichat_messages", "aichat_messages": get_aichat_message(wsinfo.info.user, session), "message": "chat changed"}
                await wsinfo.websocket.send_text(json.dumps(sendJson))
                
            # 没看懂前端想干啥
            else:
                sendJson = {"type": "info", "message": "invalid message type"}
                await wsinfo.websocket.send_text(json.dumps(sendJson))
                await wsinfo.websocket.close(code=4003)
                raise WebSocketDisconnect
        except WebSocketDisconnect as e:
            raise e
        except HTTPException as e:
            sendJson = {"type": "info", "message": str(e)}
            await wsinfo.websocket.send_text(json.dumps(sendJson))
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
                    sendJson = {"type": "info", "message": "authentication failed"}
                    await websocket.send_text(json.dumps(sendJson))
                    await websocket.close(code=4003)
                    break
            elif not wsinfo:
                sendJson = {"type": "info", "message": "not authenticated"}
                await websocket.send_text(json.dumps(sendJson))
                await websocket.close(code=4003)
                raise WebSocketDisconnect
            else:
                await manager.handle_message(session, wsinfo, data)
    except WebSocketDisconnect:
        manager.disconnect(wsinfo)

