from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from fast_zero.db.connection import get_session
from fast_zero.db.models import User
from fast_zero.helpers.exceptions import CredentialsException
from fast_zero.helpers.settings import env

oauth2_scheme = OAuth2PasswordBearer(tokenUrl='/auth/token')

pwd_context = PasswordHash.recommended()


def get_password_hash(password: str):
    return pwd_context.hash(password)


def verify_password(pain_password: str, hashed_password: str):
    return pwd_context.verify(pain_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()

    expire_time = datetime.now(tz=ZoneInfo('UTC')) + timedelta(
        minutes=env.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    to_encode.update({'exp': expire_time})

    encoded_jwt = jwt.encode(to_encode, env.SECRET_KEY, env.ALGORITHM)

    return encoded_jwt


async def get_current_user(
    session: AsyncSession = Depends(get_session),
    token: str = Depends(oauth2_scheme),
):
    try:
        payload: dict = jwt.decode(token, env.SECRET_KEY, env.ALGORITHM)
        sub_email = payload.get('sub')

        if not sub_email:
            raise CredentialsException()

    except jwt.DecodeError:
        raise CredentialsException()

    except jwt.ExpiredSignatureError:
        raise CredentialsException(detail='Token has expired')

    user = await session.scalar(select(User).where(User.email == sub_email))

    if not user:
        raise CredentialsException()

    return user
