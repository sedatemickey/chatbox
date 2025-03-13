from sqlmodel import create_engine, SQLModel, Session, Field
from datetime import datetime, timezone
from typing import Annotated
from fastapi import Depends


class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(index=True, unique=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.now)
    
class Group(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    groupname: str = Field(index=True, unique=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
class GroupMember(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    groupid: int = Field(index=True)
    userid: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
class Friends(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    userid: int = Field(index=True)
    friendid: int = Field(index=True)
    created_at: datetime = Field(default_factory=datetime.now)
    
class GroupMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    senderid: int = Field(index=True)
    groupid: int = Field(index=True)
    message: str
    created_at: datetime = Field(default_factory=datetime.now)
    
class PrivateMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    senderid: int = Field(index=True)
    receiverid: int = Field(index=True)
    message: str
    created_at: datetime = Field(default_factory=datetime.now)
    
class AichatMessage(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    user_id: int = Field(index=True)
    message_type: str
    message: str
    created_at: datetime = Field(default_factory=datetime.now)


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, connect_args=connect_args)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

SessionDepend = Annotated[Session, Depends(get_session)]

