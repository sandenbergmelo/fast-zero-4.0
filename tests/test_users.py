from fastapi import status
from fastapi.testclient import TestClient

from fast_zero.schemas.schemas import UserPublic


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


def test_update_user_integrity_error(
    client: TestClient,
    user,
    other_user,
    token,
):
    response = client.put(
        f'/users/{user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={
            'username': other_user.username,
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
