from openai import OpenAI
import os
from fastapi import APIRouter, HTTPException, status, Depends

client = OpenAI(api_key="WTY_AK_IOI", base_url=os.environ['AICHAT_API_URL']+"/v1/")
router = APIRouter()

@router.post("/chat")

def chat(text, messages, model = "deepseek-resonser"):
    print(os.environ['AICHAT_API_URL']+"/v1/")
    AichatMessage = [{"role": "user" if message["type"] == "sent" else "assistant", "content": message["message"]} for message in messages]
    AichatMessage.append({"role": "user", "content": text})
    
    response = client.chat.completions.create(
        model=model,
        messages=AichatMessage,
        stream=True
    )
    for chunk in response:
        yield chunk.choices[0].delta.content
    
