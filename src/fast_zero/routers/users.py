from typing import Annotated

from fastapi import APIRouter, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.db.models import User
from fast_zero.dependencies.annotated_types import T_CurrentUser, T_Session
from fast_zero.helpers.exceptions import NotFoundException, PermissionException
from fast_zero.helpers.security import get_password_hash
from fast_zero.schemas.schemas import (
    FilterPage,
    Message,
    UserPublic,
    UserSchema,
    UsersList,
)

router = APIRouter(prefix='/users', tags=['users'])


@router.get('/', status_code=status.HTTP_200_OK, response_model=UsersList)
async def get_all_users(
    _: T_CurrentUser,
    session: T_Session,
    filter: Annotated[FilterPage, Query()],
):
    users = await session.scalars(
        select(User).limit(filter.limit).offset(filter.offset)
    )
    return {'users': users}


@router.get(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
async def get_user_by_id(
    _: T_CurrentUser,
    user_id: int,
    session: T_Session,
):
    user = await session.get(User, user_id)

    if not user:
        raise NotFoundException(detail='User not found')

    return user


@router.post(
    '/',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
async def create_user(user: UserSchema, session: T_Session):
    db_user = await session.scalar(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )

    if db_user:
        if db_user.username == user.username:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Username already exists',
            )
        elif db_user.email == user.email:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail='Email already exists',
            )

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(new_user)
    await session.commit()
    await session.refresh(new_user)

    return new_user


@router.put(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
async def update_user(
    user_id: int,
    user: UserSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise PermissionException()

    try:
        current_user.username = user.username
        current_user.email = user.email
        current_user.password = get_password_hash(user.password)

        await session.commit()
        await session.refresh(current_user)

        return current_user

    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username or Email already exists',
        )


@router.delete(
    '/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
async def delete_user(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    if current_user.id != user_id:
        raise PermissionException()

    await session.delete(current_user)
    await session.commit()

    return {'message': 'User deleted'}
