from typing import Any

from fastapi import HTTPException, status


class CredentialsException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_401_UNAUTHORIZED,
        detail: Any = 'Could not validate credentials',
        headers: dict[str, str] | None = {'WWW-Authenticate': 'Bearer'},
    ) -> None:
        super().__init__(status_code, detail, headers)


class PermissionException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_403_FORBIDDEN,
        detail: Any = 'Not enough permissions',
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)


class NotFoundException(HTTPException):
    def __init__(
        self,
        status_code: int = status.HTTP_404_NOT_FOUND,
        detail: Any = 'Resource not found',
        headers: dict[str, str] | None = None,
    ) -> None:
        super().__init__(status_code, detail, headers)
