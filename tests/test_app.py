from fastapi import status
from fastapi.testclient import TestClient


def test_root_should_return_hello_world(client: TestClient):
    response = client.get('/')

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Hello, World!'}
