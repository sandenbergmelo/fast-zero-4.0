from contextlib import contextmanager
from datetime import datetime
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import event
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.pool import StaticPool

from fast_zero.app import app
from fast_zero.db.connection import get_session
from fast_zero.db.models import table_registry
from fast_zero.helpers.security import get_password_hash
from tests.factories import UserFactory


@pytest.fixture
def anyio_backend():
    return ('asyncio', {'use_uvloop': True})


@pytest.fixture
async def session(anyio_backend) -> AsyncGenerator[AsyncSession, None]:
    async_engine = create_async_engine(
        'sqlite+aiosqlite:///:memory:',
        connect_args={'check_same_thread': False},
        poolclass=StaticPool,
    )

    async_session = async_sessionmaker(
        bind=async_engine,
        class_=AsyncSession,
        expire_on_commit=False,
    )

    async with async_engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.create_all)

    async with async_session() as session:
        yield session

    async with async_engine.begin() as conn:
        await conn.run_sync(table_registry.metadata.drop_all)


@pytest.fixture
async def user(session: AsyncSession):
    clean_password = 'secret'

    user = UserFactory(password=get_password_hash(clean_password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

    user.clean_password = clean_password

    return user


@pytest.fixture
async def other_user(session: AsyncSession):
    clean_password = 'secret2'

    user = UserFactory(password=get_password_hash(clean_password))

    session.add(user)
    await session.commit()
    await session.refresh(user)

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
        '/auth/token',
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
