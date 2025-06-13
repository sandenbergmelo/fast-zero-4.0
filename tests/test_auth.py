from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from fast_zero.helpers.security import create_access_token


def test_get_current_user_not_found(client: TestClient):
    token = create_access_token({'sub': 'no_user@no_user.com'})

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_get_token(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={
            'username': user.email,
            'password': user.clean_password,
        },
    )

    response_body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert response_body['token_type'] == 'Bearer'
    assert 'access_token' in response_body


def test_token_wrong_email(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': 'incorrect', 'password': user.clean_password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_password(client: TestClient, user):
    response = client.post(
        '/auth/token',
        data={'username': user.email, 'password': 'incorrect'},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_jwt_invalid_token(client: TestClient):
    response = client.delete(
        '/users/1',
        headers={'Authorization': 'Bearer invalid-token'},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_with_no_sub(client: TestClient, user):
    token = create_access_token({'sub': ''})

    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}


def test_token_expired_after_time(client: TestClient, user):
    with freeze_time('2025-11-29 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2025-11-29 12:30:01'):
        response = client.put(
            f'/users/{user.id}',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'username': 'test',
                'email': 'test@test.test',
                'password': 'test',
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Token has expired'}


def test_refresh_token(client: TestClient, user, token):
    response = client.post(
        '/auth/refresh_token',
        headers={'Authorization': f'Bearer {token}'},
    )

    data = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert 'access_token' in data
    assert 'token_type' in data
    assert data['token_type'] == 'Bearer'


def test_token_expired_should_not_refresh(client: TestClient, user):
    with freeze_time('2025-11-29 12:00:00'):
        response = client.post(
            '/auth/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2025-11-29 12:30:01'):
        response = client.post(
            '/auth/refresh_token',
            headers={'Authorization': f'Bearer {token}'},
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {'detail': 'Token has expired'}
