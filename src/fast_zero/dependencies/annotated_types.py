from typing import Annotated

from fastapi import Depends
from sqlalchemy.orm import Session

from fast_zero.db.connection import get_session

T_Session = Annotated[Session, Depends(get_session)]
