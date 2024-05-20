from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status
from starlette.exceptions import HTTPException
from starlette.status import HTTP_200_OK

from db.config import get_async_session
from .models import UserAuth
from .utils import authenticate_user, create_access_token
from fastapi import APIRouter

router = APIRouter(prefix="/login", tags=["login"])


@router.post("", status_code=HTTP_200_OK, summary="Auth user")
async def login_for_access_token(data: UserAuth, session: AsyncSession = Depends(get_async_session)):
    user = await authenticate_user(session, data.username, data.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": user.username}
    )
    return {"access_token": access_token, "token_type": "bearer"}
