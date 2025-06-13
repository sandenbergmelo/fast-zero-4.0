from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from fast_zero.db.models import User
from fast_zero.dependencies.annotated_types import (
    T_CurrentUser,
    T_OAuthForm,
    T_Session,
)
from fast_zero.helpers.security import create_access_token, verify_password
from fast_zero.schemas.schemas import Token

router = APIRouter(prefix='/auth', tags=['auth'])


@router.post(
    '/token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
async def login_from_access_token(session: T_Session, form_data: T_OAuthForm):
    incorrect_data_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect email or password',
    )

    user = await session.scalar(
        select(User).where(User.email == form_data.username)
    )

    if not user:
        raise incorrect_data_exception

    if not verify_password(form_data.password, user.password):
        raise incorrect_data_exception

    token = create_access_token({'sub': user.email})

    return {'access_token': token, 'token_type': 'Bearer'}


@router.post('/refresh_token')
async def refresh_access_token(user: T_CurrentUser):
    new_access_token = create_access_token(data={'sub': user.email})

    return {'access_token': new_access_token, 'token_type': 'Bearer'}
