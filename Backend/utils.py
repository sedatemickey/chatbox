from database import User, Group, GroupMember, Friends, GroupMessage, PrivateMessage, SessionDepend
from sqlmodel import select, exists, or_, and_
from fastapi import HTTPException, status


def get_message_by_userid(user_id, user, session: SessionDepend):
    db_messages = session.exec(
        select(PrivateMessage).where(
            or_(
                and_(PrivateMessage.senderid == user_id, PrivateMessage.receiverid == user.id),
                and_(PrivateMessage.senderid == user.id, PrivateMessage.receiverid == user_id)
            )
        )
    ).all()
    db_messages.sort(key=lambda x: x.created_at, reverse=False)
    return [{"message": message.message, "type": "sent" if message.senderid == user.id  else "received", "created_at": message.created_at.timestamp() * 1000} for message in db_messages]

def save_private_message(user: User, friend_id: int, message: str, session: SessionDepend): 
    exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Private message saving failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        friends_id = [friend["id"] for friend in get_friends_list(user, session)]
        if not friend_id in friends_id:
            exception.detail = "Friend does not exist"
            raise exception
        db_message = PrivateMessage(senderid=user.id, receiverid=friend_id, message=message)
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return db_message
    except Exception as e:
        print(e)
        raise exception

def get_friends_list(user: User, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="get_friends_list failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_friends = session.exec(
            select(Friends).where(Friends.userid == user.id)
        ).all()
        friends_id = [db.friendid for db in db_friends]
        db_friends = session.exec(
            select(Friends).where(Friends.friendid == user.id)
        ).all()
        friends_id.extend([db.userid for db in db_friends])
        
        friends = []
        for friend_id in friends_id:
            friend_name = session.exec(
                select(User).where(User.id == friend_id)
            ).first().username
            friend_message = get_message_by_userid(friend_id, user, session)
            if len(friend_message) > 0:
                friend_message = friend_message[-1]
            else:
                friend_message = {"message": "", "type": ""}
            friends.append({"id": friend_id, "username": friend_name, "last_message": friend_message})
        return friends
    except:
        raise exception

def add_friend(user: User, friendName: str, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Friend addition failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        friend_id = session.exec(   
            select(User).where(User.username == friendName)
        ).first().id
        if friend_id is None:
            exception.detail = "Friend does not exist"
            raise exception
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
        return {"message": "Friend added successfully", "friend_id": friend_id}
    except:
        raise exception

def remove_friend(user: User, friend_id: int, session: SessionDepend):
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
    

def get_message_by_groupid(user: User, group_id: int, session: SessionDepend):
    db_messages = session.exec(
        select(GroupMessage).where(GroupMessage.groupid == group_id)
    ).all()
    db_messages.sort(key=lambda x: x.created_at, reverse=False)
    return [{"message": message.message, "sender": message.senderid, "type": "sent" if message.senderid == user.id  else "received", "created_at": message.created_at.timestamp() * 1000} for message in db_messages]

def save_group_message(user: User, group_id: int, message, session: SessionDepend):
    exception = HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Group message saving failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    try:
        groups_id = [group["id"] for group in get_group_list(user, session)]
        if not group_id in groups_id:
            exception.detail = "Group does not exist"
            raise exception
        db_message = GroupMessage(senderid=user.id, groupid=group_id, message=message)
        session.add(db_message)
        session.commit()
        session.refresh(db_message)
        return db_message
    except Exception as e:
        print(e)
        raise exception

def get_group_list(user: User, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="get_group_list failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_groups = session.exec(
            select(GroupMember).where(GroupMember.userid == user.id)
        ).all()
        groups_id = [db.groupid for db in db_groups]
        groups = []
        for group_id in groups_id:
            group = session.exec(
                select(Group).where(Group.id == group_id)
            ).first()
            group_message = get_message_by_groupid(user, group_id, session)
            if len(group_message) > 0:
                group_message = group_message[-1]
            else:
                group_message = {"message": "", "sender": "", "type": ""}
            groups.append({"id": group.id, "groupname": group.groupname, "last_message": group_message})
        return groups
    except Exception as e:
        print(e)
        raise exception

def create_group(user: User, group_name: str, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="Group creation failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try: 
        db_group = Group(groupname=group_name)
        session.add(db_group)
        session.commit()
        session.refresh(db_group)
        db_group_member = GroupMember(userid=user.id, groupid=db_group.id)
        session.add(db_group_member)
        session.commit()
        session.refresh(db_group_member)
        return db_group
    except:
        raise exception

def add_user_to_group(user: User, group_id: int, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="User addition to group failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        group_exists = session.exec(
            select(Group).where(Group.id == group_id)
        ).first()
        if group_exists is None:
            exception.detail = "Group does not exist"
            raise exception
        db_group_member = session.exec(
            select(GroupMember).where(
                and_(GroupMember.userid == user.id, GroupMember.groupid == group_id)
            )
        ).first()
        if db_group_member is not None:
            exception.detail = "User is already a member of the group"
            raise exception
        db_group_member = GroupMember(userid=user.id, groupid=group_id)
        session.add(db_group_member)
        session.commit()
        session.refresh(db_group_member)
        return "User added to group successfully"
    except:
        raise exception

def remove_user_from_group(user: User, group_id: int, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="User removal from group failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_group_member = session.exec(
            select(GroupMember).where(
                and_(GroupMember.userid == user.id, GroupMember.groupid == group_id)
            )
        ).first()
        if db_group_member is None:
            exception.detail = "User is not a member of the group"
            raise exception
        session.delete(db_group_member)
        session.commit()
        return "User removed from group successfully"
    except:
        raise exception

def get_all_groups_list(user: User, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="get_all_groups_list failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_groups = session.exec(
            select(Group)
        ).all()
        groups = []
        for db_group in db_groups:
            groups.append({"id": db_group.id, "groupname": db_group.groupname})
        return groups
    except Exception as e:
        print(e)
        raise exception
    
def get_all_users_list(user: User, session: SessionDepend):
    exception = HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        detail="get_all_users_list failed",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        db_users = session.exec(
            select(User)
        ).all()
        users = []
        for db_user in db_users:
            if db_user.id != user.id:
                users.append({"id": db_user.id, "username": db_user.username})
        return users
    except Exception as e:
        print(e)
        raise exception