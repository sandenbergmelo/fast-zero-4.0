from fastapi import FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from fast_zero.db.models import User
from fast_zero.dependencies.annotated_types import (
    T_CurrentUser,
    T_OAuthForm,
    T_Session,
)
from fast_zero.helpers.exceptions import NotFoundException, PermissionException
from fast_zero.helpers.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from fast_zero.schemas.schemas import (
    Message,
    Token,
    UserPublic,
    UserSchema,
    UsersList,
)

app = FastAPI()


@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


@app.get('/users', status_code=status.HTTP_200_OK, response_model=UsersList)
def get_all_users(
    current_user: T_CurrentUser,
    session: T_Session,
    limit: int = 10,
    offset: int = 0,
):
    users = session.scalars(select(User).limit(limit).offset(offset))
    return {'users': users}


@app.get(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def get_user_by_id(
    user_id: int,
    session: T_Session,
    current_user: T_CurrentUser,
):
    user = session.get(User, user_id)

    if not user:
        raise NotFoundException(detail='User not found')

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

    new_user = User(
        username=user.username,
        email=user.email,
        password=get_password_hash(user.password),
    )

    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@app.put(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def update_user(
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

        session.commit()
        session.refresh(current_user)

        return current_user

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
def delete_user(user_id: int, session: T_Session, current_user: T_CurrentUser):
    if current_user.id != user_id:
        raise PermissionException()

    session.delete(current_user)
    session.commit()

    return {'message': 'User deleted'}


@app.post(
    '/token',
    status_code=status.HTTP_200_OK,
    response_model=Token,
)
def login_from_access_token(session: T_Session, form_data: T_OAuthForm):
    incorrect_data_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail='Incorrect email or password',
    )

    user = session.scalar(select(User).where(User.email == form_data.username))

    if not user:
        raise incorrect_data_exception

    if not verify_password(form_data.password, user.password):
        raise incorrect_data_exception

    token = create_access_token({'sub': user.email})

    return {'access_token': token, 'token_type': 'Bearer'}
