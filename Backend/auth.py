from dotenv import load_dotenv
import os
from passlib.context import CryptContext
from datetime import timedelta, datetime
from fastapi.security import OAuth2PasswordBearer
import jwt
from fastapi import Depends, HTTPException, status
from database import SessionDepend, User
from sqlmodel import select

load_dotenv()

JWT_SECRET_KEY = os.getenv('JWT_SECRET_KEY')
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login") #!!

def get_password_hash(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, JWT_SECRET_KEY, algorithm=ALGORITHM)

# async def get_current_user(token: str = Depends(oauth2_scheme)):
def get_current_user(token: str, session: SessionDepend):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("username")
        if not username:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = session.exec(
        select(User).where(User.username == username)
    ).first()
    if user is None:
        raise credentials_exception
    return user