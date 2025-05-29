from fastapi import status
from fastapi.testclient import TestClient
from freezegun import freeze_time

from fast_zero.helpers.security import create_access_token
from fast_zero.schemas.schemas import UserPublic


def test_root_should_return_hello_world(client: TestClient):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello, World!'}


def test_create_user(client: TestClient):
    response = client.post(
        '/users',
        json={
            'username': 'JohnDoe',
            'email': 'johndoe@email.com',
            'password': 'supersecretpassword',
        },
    )

    assert response.status_code == status.HTTP_201_CREATED
    assert response.json() == {
        'id': 1,
        'username': 'JohnDoe',
        'email': 'johndoe@email.com',
    }


def test_create_user_username_already_exists(client: TestClient, user):
    response = client.post(
        '/users',
        json={
            'username': user.username,
            'email': 'different@email.com',
            'password': 'does not matter',
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Username already exists'}


def test_create_user_email_already_exists(client: TestClient, user):
    response = client.post(
        '/users',
        json={
            'username': 'Different Username',
            'email': user.email,
            'password': 'does not matter',
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Email already exists'}


def test_get_all_users(client: TestClient, user, other_user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    other_user_schema = UserPublic.model_validate(other_user).model_dump()

    response = client.get(
        '/users',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'users': [user_schema, other_user_schema]}


def test_get_user_by_id(client: TestClient, user, token):
    user_schema = UserPublic.model_validate(user).model_dump()
    response = client.get(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == user_schema


def test_get_non_existing_user_by_id(client: TestClient, user, token):
    response = client.get(
        f'/users/{user.id + 1}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client: TestClient, user, token):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'JohnDoeEdited',
            'email': 'johndoeedited@email.com',
            'password': 'supersecretpassword',
        },
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'username': 'JohnDoeEdited',
        'email': 'johndoeedited@email.com',
    }


def test_update_wrong_user(client: TestClient, other_user, token):
    response = client.put(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'JohnDoeEdited',
            'email': 'johndoeedited@email.com',
            'password': 'supersecretpassword',
        },
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_update_user_integrity_error(client: TestClient, user, token):
    client.post(
        '/users',
        json={
            'username': 'other',
            'email': 'other@example.com',
            'password': 'secret',
        },
    )

    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': 'other',
            'email': 'bob@example.com',
            'password': 'secret',
        },
    )

    assert response.status_code == status.HTTP_409_CONFLICT
    assert response.json() == {'detail': 'Username or Email already exists'}


def test_delete_user(client: TestClient, user, token):
    response = client.delete(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_wrong_user(client: TestClient, other_user, token):
    response = client.delete(
        f'/users/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert response.json() == {'detail': 'Not enough permissions'}


def test_get_token(client: TestClient, user):
    response = client.post(
        '/token',
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
        '/token',
        data={'username': 'incorrect', 'password': user.clean_password},
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Incorrect email or password'}


def test_token_wrong_password(client: TestClient, user):
    response = client.post(
        '/token',
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
    with freeze_time('2025-05-28 12:00:00'):
        response = client.post(
            '/token',
            data={'username': user.email, 'password': user.clean_password},
        )

        assert response.status_code == status.HTTP_200_OK
        token = response.json()['access_token']

    with freeze_time('2025-05-28 12:31:00'):
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


def test_get_current_user_not_found(client: TestClient):
    token = create_access_token({'sub': 'no_user@no_user.com'})

    response = client.delete(
        '/users/1', headers={'Authorization': f'Bearer {token}'}
    )

    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert response.json() == {'detail': 'Could not validate credentials'}
