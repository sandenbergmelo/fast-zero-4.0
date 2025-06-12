from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio.session import AsyncSession

from fast_zero.db.connection import get_session
from fast_zero.db.models import User
from fast_zero.helpers.security import get_current_user

T_Session = Annotated[AsyncSession, Depends(get_session)]
T_OAuthForm = Annotated[OAuth2PasswordRequestForm, Depends()]
T_CurrentUser = Annotated[User, Depends(get_current_user)]
