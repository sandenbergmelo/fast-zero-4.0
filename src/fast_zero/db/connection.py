from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from fast_zero.helpers.settings import env

engine = create_engine(env.DATABASE_URL)


def get_session():
    with Session(engine) as session:  # pragma: no cover
        yield session
