from database import User, Group, GroupMember, Friends, GroupMessage, PrivateMessage, SessionDepend
from sqlmodel import select, exists, or_, and_
from fastapi import HTTPException, status

# 未测试！！
def get_message_by_userid(user_id, user, session: SessionDepend):
    db_messages = session.exec(
        select(PrivateMessage).where(
            or_(
                and_(PrivateMessage.senderid == user_id, PrivateMessage.receiverid == user.id),
                and_(PrivateMessage.senderid == user.id, PrivateMessage.receiverid == user_id)
            )
        )
    ).all()
    return [{"message": message.message, "type": "sent" if message.senderid == user.id  else "received"} for message in db_messages]

def get_friends_list(user, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="get_friends_list failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_friends = session.exec(
            select(Friends).where(Friends.userid == user.id)
        ).all()
        friends = [db.friendid for db in db_friends]
        db_friends = session.exec(
            select(Friends).where(Friends.friendid == user.id)
        ).all()
        friends.extend([db.userid for db in db_friends])
        return friends
    except:
        raise exception

def add_friend(user, friend_id, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Friend addition failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        if user.id == friend_id:
            exception.detail = "You cannot add yourself as a friend"
            raise exception
        friend_exists = session.exec(
            select(Friends).where(
                or_(
                    and_(Friends.userid == friend_id , Friends.friendid == user.id), 
                    and_(Friends.userid == user.id , Friends.friendid == friend_id)
                )
            )
        ).first()
        if friend_exists is not None:
            exception.detail = "Friend already exists"
            raise exception
        db_friend = Friends(userid=user.id, friendid=friend_id)
        session.add(db_friend)
        session.commit()
        session.refresh(db_friend)
        return "Friend added successfully"
    except:
        raise exception

def remove_friend(user, friend_id, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Friend removal failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_friend = session.exec(
            select(Friends).where(
                or_(
                    and_(Friends.userid == friend_id , Friends.friendid == user.id), 
                    and_(Friends.userid == user.id , Friends.friendid == friend_id)
                )
            )
        ).first()
        if db_friend is None:
            exception.detail = "Friend does not exist"
            raise exception
        session.delete(db_friend)
        session.commit()
        return "Friend removed successfully"
    except:
        raise exception
    
def get_message_by_groupid(group_id):
    pass

def get_group_list(user):
    pass

def create_group(user, group_name):
    pass

def add_user_to_group(user, group_id):
    pass

def remove_user_from_group(user, group_id):
    pass

