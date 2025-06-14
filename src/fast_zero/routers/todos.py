from typing import Annotated

from fastapi import APIRouter, Query, status
from sqlalchemy import select

from fast_zero.db.models import Todo
from fast_zero.dependencies.annotated_types import T_CurrentUser, T_Session
from fast_zero.helpers.exceptions import NotFoundException
from fast_zero.schemas.schemas import (
    FilterTodo,
    Message,
    TodoList,
    TodoPublic,
    TodoSchema,
    TodoUpdate,
)

router = APIRouter(prefix='/todos', tags=['todos'])


@router.post(
    '/',
    response_model=TodoPublic,
    status_code=status.HTTP_201_CREATED,
)
async def create_todo(
    todo: TodoSchema,
    session: T_Session,
    current_user: T_CurrentUser,
):
    new_todo = Todo(
        **todo.model_dump(),
        user_id=current_user.id,
    )

    session.add(new_todo)
    await session.commit()
    await session.refresh(new_todo)

    return new_todo


@router.get(
    '/',
    response_model=TodoList,
    status_code=status.HTTP_200_OK,
)
async def get_todos(
    current_user: T_CurrentUser,
    session: T_Session,
    filter: Annotated[FilterTodo, Query()],
):
    query = select(Todo).where(Todo.user_id == current_user.id)

    if filter.title:
        query = query.filter(Todo.title.contains(filter.title))

    if filter.description:
        query = query.filter(Todo.description.contains(filter.description))

    if filter.state:
        query = query.filter(Todo.state == filter.state)

    todos = await session.scalars(
        query.offset(filter.offset).limit(filter.limit)
    )

    return {'todos': todos.all()}


@router.patch('/{todo_id}', response_model=TodoPublic)
async def patch_todo(
    todo_id: int,
    session: T_Session,
    user: T_CurrentUser,
    todo: TodoUpdate,
):
    db_todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not db_todo:
        raise NotFoundException(detail='Task not found')

    for key, value in todo.model_dump(exclude_unset=True).items():
        setattr(db_todo, key, value)

    session.add(db_todo)
    await session.commit()
    await session.refresh(db_todo)

    return db_todo


@router.delete('/{todo_id}', response_model=Message)
async def delete_todo(todo_id: int, session: T_Session, user: T_CurrentUser):
    todo = await session.scalar(
        select(Todo).where(Todo.user_id == user.id, Todo.id == todo_id)
    )

    if not todo:
        raise NotFoundException(detail='Task not found')

    await session.delete(todo)

    return {'message': 'Task has been deleted successfully'}
