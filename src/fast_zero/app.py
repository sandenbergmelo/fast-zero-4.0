from fastapi import FastAPI, status

from fast_zero.routers import auth, users
from fast_zero.schemas.schemas import Message

app = FastAPI()


@app.get('/', status_code=status.HTTP_200_OK, response_model=Message)
def read_root():
    return {'message': 'Hello, World!'}


app.include_router(auth.router)
app.include_router(users.router)
