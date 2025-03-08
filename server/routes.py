from fastapi import APIRouter, HTTPException, status, Form
from database import SessionDepend, User
# from pydantic import BaseModel
from auth import verify_password, create_access_token, get_password_hash
from sqlmodel import select

router = APIRouter()

@router.post("/auth/register")
def register(
    session: SessionDepend,
    username: str = Form("username"), 
    password: str = Form("password")
):
    db_user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(password)
    new_user = User(username=username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    access_token = create_access_token({"username": username})
    return {"access_token": access_token, "token_type": "bearer"} 

@router.post("/auth/login")
def login(
    session: SessionDepend,
    username: str = Form("username"), 
    password: str = Form("password")
):
    db_user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if not db_user or not verify_password(password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token({"username": username})
    return {"access_token": access_token, "token_type": "bearer"} 