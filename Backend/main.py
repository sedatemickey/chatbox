from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from database import create_db_and_tables
from routes import router
from message import wsrouter
from dotenv import load_dotenv
import os

app = FastAPI()
FRONTEND_URL = os.getenv("FRONTEND_URL")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[FRONTEND_URL],  
    allow_credentials=True,                   
    allow_methods=["*"],                      
    allow_headers=["*"],                      
)

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

app.include_router(router)
app.include_router(wsrouter)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=5100, reload=True)