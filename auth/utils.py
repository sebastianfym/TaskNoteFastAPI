from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException

from auth.models import UserInDB
from db.config import get_async_session
# from users.models import User
from db.models import User

# from .schemas import TokenData

SECRET_KEY = "cf6746bcd1a258d8c6736dbf5fa016e59b82d5608b1a337b0c24c45501099bd6"  #openssl rand -hex 32
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode.update()
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def authenticate_user(session: AsyncSession, username: str, password: str) -> User:
    user = await session.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def get_current_user(token: str = Depends(oauth2_scheme), session: AsyncSession = Depends(get_async_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = await session.execute(select(User).where(User.username == username))
    user = user.scalars().first()
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(current_user: User = Depends(get_current_user)):
    return current_user


async def get_user(db_session: AsyncSession, user_id: int):
    user = await db_session.execute(select(User).where(User.id == user_id))
    return user.scalar()


async def get_user_by_username(db_session: AsyncSession, username: str):
    user = await db_session.execute(select(User).where(User.username == username))
    return user.scalar()
