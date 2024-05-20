from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.exceptions import HTTPException
from starlette.status import HTTP_201_CREATED

from auth.models import UserAuth
from auth.utils import get_password_hash
from db.models import User
from db.service import get_session, get_user_by_username
from fastapi import APIRouter

from tasks.models import ErrorException

router = APIRouter(prefix="/register", tags=["register"])


@router.post("", status_code=HTTP_201_CREATED, summary="Create user", responses={
                400: {"model": ErrorException, "detail": "Username already registered",
                      "message": "Username already registered"}})
async def register(user: UserAuth, session: AsyncSession = Depends(get_session)):
    check_user = await get_user_by_username(session, user.username)
    if check_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    password_hash = get_password_hash(user.password)

    new_user = User(username=user.username, password_hash=password_hash)

    session.add(new_user)
    await session.commit()

    return new_user