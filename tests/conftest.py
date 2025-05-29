from contextlib import contextmanager
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.db.connection import get_session
from fast_zero.db.models import User, table_registry
from fast_zero.helpers.security import get_password_hash


@pytest.fixture
def session():
    engine = create_engine(
        'sqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )
    table_registry.metadata.create_all(engine)

    with Session(engine) as session:
        yield session

    table_registry.metadata.drop_all(engine)


@pytest.fixture
def user(session: Session):
    clean_password = 'secret'

    user = User(
        username='JohnDoe',
        email='johndoe@email.com',
        password=get_password_hash(clean_password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = clean_password

    return user


@pytest.fixture
def other_user(session: Session):
    clean_password = 'secret2'

    user = User(
        username='JohnDoe2',
        email='johndoe2@email.com',
        password=get_password_hash(clean_password),
    )

    session.add(user)
    session.commit()
    session.refresh(user)

    user.clean_password = clean_password

    return user


@pytest.fixture
def client(session):
    with TestClient(app) as client:
        app.dependency_overrides[get_session] = lambda: session
        yield client

    app.dependency_overrides.clear()


@pytest.fixture
def token(client: TestClient, user) -> str:
    response = client.post(
        '/token',
        data={'username': user.email, 'password': user.clean_password},
    )

    return response.json()['access_token']


@contextmanager
def _mock_db_time(*, model, time=datetime(2025, 1, 1)):
    def fake_time_hook(mapper, connection, target):
        if hasattr(target, 'created_at'):
            target.created_at = time

        if hasattr(target, 'updated_at'):
            target.updated_at = time

    event.listen(model, 'before_insert', fake_time_hook)
    yield time
    event.remove(model, 'before_insert', fake_time_hook)


@pytest.fixture
def mock_db_time():
    return _mock_db_time
