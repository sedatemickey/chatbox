from fastapi import APIRouter, HTTPException, status, Form
from database import SessionDepend, User
# from pydantic import BaseModel
from auth import verify_password, create_access_token, get_password_hash, get_current_user
from sqlmodel import select
from pydantic import BaseModel

class UserPass(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    token: str

router = APIRouter()

@router.post("/auth/register")
def register(
    user_pass: UserPass,
    session: SessionDepend
):
    db_user = session.exec(
        select(User).where(User.username == user_pass.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = get_password_hash(user_pass.password)
    new_user = User(username=user_pass.username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    access_token = create_access_token({"username": user_pass.username})
    return {"access_token": access_token, "token_type": "bearer"} 

@router.post("/auth/login")
def login(
    user_pass: UserPass,
    session: SessionDepend
):
    db_user = session.exec(
        select(User).where(User.username == user_pass.username)
    ).first()
    if not db_user or not verify_password(user_pass.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )
    access_token = create_access_token({"username": user_pass.username})
    return {"access_token": access_token, "token_type": "bearer"} 

@router.post("/auth/refresh_token")
def refresh_token(
    old_token: Token,
    session: SessionDepend
):
    try:
        user = get_current_user(old_token.token, session)
    except HTTPException as e:
        return e
    print("user::::",user)
    access_token = create_access_token({"username": user.username})
    return {"access_token": access_token, "token_type": "bearer"} 

# @router.get("/user/groups/list")
# def list_groups(session: SessionDepend, current_user: User = Depends(get_current_user)):
#     return