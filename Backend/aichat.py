from openai import OpenAI
import os
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import StreamingResponse
from database import SessionDepend, User
from auth import get_current_user
from utils import save_aichat_message, get_aichat_message
import json
from pydantic import BaseModel

client = OpenAI(api_key="WTY_AK_IOI", base_url=os.environ['AICHAT_API_URL']+"/v1/")
airouter = APIRouter()

class AichatMessage(BaseModel):
    message: str

@airouter.post("/aichat")
async def handle_chat(aichat_message: AichatMessage, session: SessionDepend, user: User = Depends(get_current_user)):
    return StreamingResponse(
        chat_generator(aichat_message, session, user),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive"
        }
    )
    
def chat_generator(aichat_message: AichatMessage, session: SessionDepend, user: User):
    chatSession = chat(aichat_message.message, get_aichat_message(user, session))
    save_aichat_message(user, aichat_message.message, "sent", session)
    received = ""
    for chunk in chatSession:
        received += chunk
        yield chunk
    save_aichat_message(user, received, "received", session)

def chat(text, messages, model = "deepseek-resonser"):
    print(os.environ['AICHAT_API_URL']+"/v1/")
    AichatMessage = [{"role": "user" if message["type"] == "sent" else "assistant", "content": message["message"]} for message in messages]
    AichatMessage.append({"role": "user", "content": text})
    # print("AichatMessage: ", AichatMessage)
    response = client.chat.completions.create(
        model=model,
        messages=AichatMessage,
        stream=True
    )
    for chunk in response:
        yield chunk.choices[0].delta.content
    
