from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio.session import AsyncSession

from fast_zero.db.models import User


async def test_create_user(session: AsyncSession, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='test', email='test@test.com', password='secret')

        session.add(user)
        await session.commit()

        fetched_user = await session.scalar(select(User).where(User.id == 1))

    assert asdict(fetched_user) == {  # type: ignore
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }
