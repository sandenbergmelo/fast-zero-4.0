import asyncio
import sys

from fastapi import FastAPI, status

from fast_zero.routers import auth, todos, users
from fast_zero.schemas.schemas import Message

if sys.platform == 'win32':  # pragma: no cover
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()


@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
async def read_root():
    return {'message': 'Hello, World!'}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(todos.router)
