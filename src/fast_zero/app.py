from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.db.models import User
from fast_zero.dependencies.annotated_types import T_Session
from fast_zero.schemas.schemas import (
    Message,
    UserPublic,
    UserSchema,
    UsersList,
)

app = FastAPI()


@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


@app.get('/users', status_code=status.HTTP_200_OK, response_model=UsersList)
def get_all_users(session: T_Session, limit: int = 10, offset: int = 0):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.get(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def get_user_by_id(user_id: int, session: T_Session):
    user = session.get(User, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return user


@app.post(
    '/users',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
def create_user(user: UserSchema, session: T_Session):
    db_user = session.scalar(
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

    new_user = User(**user.model_dump())

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@app.put(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def update_user(user_id: int, user: UserSchema, session: T_Session):
    user_to_update = session.scalar(select(User).where(User.id == user_id))

    if not user_to_update:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    try:
        user_to_update.username = user.username
        user_to_update.email = user.email
        user_to_update.password = user.password

        session.commit()
        session.refresh(user_to_update)

        return user_to_update
    except IntegrityError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail='Username or Email already exists',
        )


@app.delete(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def delete_user(user_id: int, session: T_Session):
    user_to_delete = session.scalar(select(User).where(User.id == user_id))

    if not user_to_delete:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    session.delete(user_to_delete)
    session.commit()

    return {'message': 'User deleted'}
