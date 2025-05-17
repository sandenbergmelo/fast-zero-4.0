from fastapi import FastAPI, HTTPException, status

from fast_zero.schemas.schemas import (
    Message,
    UserDB,
    UserPublic,
    UserSchema,
    UsersList,
)

app = FastAPI()

database: list[UserDB] = []


@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


@app.get('/users', status_code=status.HTTP_200_OK, response_model=UsersList)
def get_all_users():
    return {'users': database}


@app.get(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def get_user_by_id(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    return database[user_id - 1]


@app.post(
    '/users',
    status_code=status.HTTP_201_CREATED,
    response_model=UserPublic,
)
def create_user(user: UserSchema):
    db_user = UserDB(**user.model_dump(), id=len(database) + 1)
    database.append(db_user)

    return db_user


@app.put(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=UserPublic,
)
def update_user(user_id: int, user: UserSchema):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    updated_user = UserDB(**user.model_dump(), id=user_id)
    database[user_id - 1] = updated_user

    return updated_user


@app.delete(
    '/users/{user_id}',
    status_code=status.HTTP_200_OK,
    response_model=Message,
)
def delete_user(user_id: int):
    if user_id > len(database) or user_id < 1:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail='User not found'
        )

    del database[user_id - 1]

    return {'message': 'User deleted'}
