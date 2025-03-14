from fastapi import APIRouter, HTTPException, status, Depends
from database import SessionDepend, User
from auth import verify_password, create_access_token, get_password_hash, get_current_user, get_current_user_by_token
from sqlmodel import select
from pydantic import BaseModel
from auth import ACCESS_TOKEN_EXPIRE_MINUTES
from utils import get_friends_list, get_group_list, get_message_by_groupid, get_message_by_userid, add_friend, remove_friend, create_group, add_user_to_group, remove_user_from_group, get_all_users_list, get_all_groups_list

class UserPass(BaseModel):
    username: str
    password: str
    
class Token(BaseModel):
    token: str
    
class UserID(BaseModel):
    user_id: int
    
class GroupID(BaseModel):
    group_id: int
    
class GroupName(BaseModel):
    groupname: str
    
class Username(BaseModel):
    username: str
    

router = APIRouter()

@router.post("/auth/register")
async def register(
    user_pass: UserPass,
    session: SessionDepend
):
    db_user = session.exec(
        select(User).where(User.username == user_pass.username)
    ).first()
    if db_user:
        raise HTTPException(status_code=422, detail="Username already registered")
    hashed_password = get_password_hash(user_pass.password)
    new_user = User(username=user_pass.username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    access_token = create_access_token({"username": user_pass.username})
    return {"access_token": access_token, "token_type": "bearer", "expires": ACCESS_TOKEN_EXPIRE_MINUTES} 

@router.post("/auth/login")
async def login(
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
    return {"access_token": access_token, "token_type": "bearer", "expires": ACCESS_TOKEN_EXPIRE_MINUTES} 

@router.post("/auth/refresh_token")
async def refresh_token(session: SessionDepend, user: User = Depends(get_current_user)):
    access_token = create_access_token({"username": user.username})
    return {"access_token": access_token, "token_type": "bearer", "expires": ACCESS_TOKEN_EXPIRE_MINUTES} 

@router.get("/user/profile")
async def get_user_profile(session: SessionDepend, user: User = Depends(get_current_user)):
    return {"username": user.username, "id": user.id}

@router.get("/user/friends/list")
async def list_friends(session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        friends = get_friends_list(user, session)
        return {"friends": friends}
    except HTTPException as e:
        raise e

@router.post("/user/friends/add")
async def add_friend_to_user(username: Username, session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        result = add_friend(user, username.username, session)
        return {"message": result["message"], "friend_id": result["friend_id"]}
    except HTTPException as e:
        raise e

@router.delete("/user/friends/delete")
async def remove_friend_from_user(user_id: UserID, session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        message = remove_friend(user, user_id.user_id, session)
        return {"message": message}
    except HTTPException as e:
        raise e

@router.get("/user/fulllist")
async def list_groups(session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        users = get_all_users_list(user, session)
        return {"users": users}
    except HTTPException as e:
        raise e
    
@router.get("/user/groups/fulllist")
async def list_groups(session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        groups = get_all_groups_list(user, session)
        return {"groups": groups}
    except HTTPException as e:
        raise e

@router.get("/user/groups/list")
async def list_groups(session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        groups = get_group_list(user, session)
        return {"groups": groups}
    except HTTPException as e:
        raise e
    
@router.post("/user/groups/create")
async def create_group_for_user(group_name: GroupName, session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        db_group = create_group(user, group_name.groupname, session)
        return {"message": "Group created successfully", "group_id": db_group.id, "groupname": db_group.groupname}
    except HTTPException as e:
        raise e
    
@router.post("/user/groups/join")
async def join_group(group_id: GroupID, session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        add_user_to_group(user, group_id.group_id, session)
        return {"message": "User added to group successfully"}
    except HTTPException as e:
        raise e
    
@router.delete("/user/groups/delete")
async def leave_group(group_id: GroupID, session: SessionDepend, user: User = Depends(get_current_user)):
    try:
        remove_user_from_group(user, group_id.group_id, session)
        return {"message": "User removed from group successfully"}
    except HTTPException as e:
        raise e
    
