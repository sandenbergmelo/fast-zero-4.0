from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from fast_zero.db.models import User


def test_create_user(session: Session, mock_db_time):
    with mock_db_time(model=User) as time:
        user = User(username='test', email='test@test.com', password='secret')

        session.add(user)
        session.commit()

        fetched_user = session.scalar(select(User).where(User.id == 1))

    assert asdict(fetched_user) == {  # type: ignore
        'id': 1,
        'username': 'test',
        'email': 'test@test.com',
        'password': 'secret',
        'created_at': time,
        'updated_at': time,
    }
