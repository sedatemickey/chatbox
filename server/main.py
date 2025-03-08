from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.security import OAuth2PasswordRequestForm
import uvicorn
from database import create_db_and_tables
from routes import router

app = FastAPI()

@app.on_event("startup")
async def startup_event():
    create_db_and_tables()

app.include_router(router)
    


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)