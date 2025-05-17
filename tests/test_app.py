from fastapi import status
from fastapi.testclient import TestClient


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


def test_get_all_users(client: TestClient):
    response = client.get('/users')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'users': [
            {'id': 1, 'username': 'JohnDoe', 'email': 'johndoe@email.com'}
        ]
    }


def test_get_user_by_id(client: TestClient):
    response = client.get('/users/1')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {
        'id': 1,
        'username': 'JohnDoe',
        'email': 'johndoe@email.com',
    }


def test_get_non_existing_user_by_id(client: TestClient):
    response = client.get('/users/999')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_update_user(client: TestClient):
    response = client.put(
        '/users/1',
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


def test_update_non_existing_user(client: TestClient):
    response = client.put(
        '/users/999',
        json={
            'username': 'JohnDoeEdited',
            'email': 'johndoeedited@email.com',
            'password': 'supersecretpassword',
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}


def test_delete_user(client: TestClient):
    response = client.delete('/users/1')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'User deleted'}


def test_delete_non_existing_user(client: TestClient):
    response = client.delete('/users/999')

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'User not found'}
