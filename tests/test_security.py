import jwt

from fast_zero.helpers.security import create_access_token
from fast_zero.helpers.settings import env


def test_jwt():
    data = {'sub': 'test'}
    token = create_access_token(data)

    decoded = jwt.decode(token, env.SECRET_KEY, env.ALGORITHM)

    assert decoded['sub'] == 'test'
    assert 'exp' in decoded
