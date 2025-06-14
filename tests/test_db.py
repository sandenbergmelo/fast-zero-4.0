from dataclasses import asdict

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from fast_zero.db.models import Todo, User


async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='test', email='test@test.com', password='secret')

        session.add(user)
        await session.commit()

        fetched_user = await session.scalar(select(User).where(User.id == 1))

    assert asdict(fetched_user) == {
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
        'todos': [],
    }


async def test_create_todo_error(session: AsyncSession, user):
    todo = Todo(
        title='Test Todo',
        description='Test Desc',
        state='test',
        user_id=user.id,
    )

    session.add(todo)
    await session.commit()

    with pytest.raises(LookupError):
        await session.scalar(select(Todo))
