from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio.session import AsyncSession

from fast_zero.db.models import Todo, TodoState
from tests.factories import TodoFactory


def test_create_todo(client, token, mock_db_time):
    with mock_db_time(model=Todo) as time:
        response = client.post(
            '/todos/',
            headers={'Authorization': f'Bearer {token}'},
            json={
                'title': 'Test todo',
                'description': 'Test todo description',
                'state': 'draft',
            },
        )

    assert response.json() == {
        'id': 1,
        'title': 'Test todo',
        'description': 'Test todo description',
        'state': 'draft',
        'created_at': time.isoformat(),
        'updated_at': time.isoformat(),
    }


async def test_list_todo_should_return_5_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 5

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos', headers={'Authorization': f'Bearer {token}'}
    )

    assert len(response.json()['todos']) == expected_todos


async def test_list_todo_pagination_should_return_2_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 2

    session.add_all(TodoFactory.create_batch(5, user_id=user.id))
    await session.commit()

    response = client.get(
        '/todos/?offset=1&limit=2',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


async def test_list_todo_filter_title_should_return_5_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 5
    title = 'Test title filter'

    session.add_all(TodoFactory.create_batch(5, title=title, user_id=user.id))
    session.add_all(TodoFactory.create_batch(2, user_id=user.id))

    await session.commit()

    response = client.get(
        f'/todos/?title={title}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


async def test_list_todo_filter_description_should_return_5_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 5
    description = 'random description'

    session.add_all(
        TodoFactory.create_batch(5, description=description, user_id=user.id)
    )
    session.add_all(TodoFactory.create_batch(2, user_id=user.id))

    await session.commit()

    response = client.get(
        f'/todos/?description={description[:4]}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


async def test_list_todo_filter_state_should_return_5_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 5
    state = TodoState.done

    session.add_all(TodoFactory.create_batch(5, state=state, user_id=user.id))
    session.add_all(
        TodoFactory.create_batch(2, state=TodoState.doing, user_id=user.id)
    )

    await session.commit()

    response = client.get(
        f'/todos/?state={state.value}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


async def test_list_todos_filter_combined_should_return_5_todos(
    session: AsyncSession, client: TestClient, user, token
):
    expected_todos = 5
    title = 'Test todo combined'
    description = 'combined description'
    state = TodoState.done

    session.add_all(
        TodoFactory.create_batch(
            5,
            user_id=user.id,
            title=title,
            description=description,
            state=state,
        )
    )
    session.add_all(TodoFactory.create_batch(2, user_id=user.id))
    session.add_all(
        TodoFactory.create_batch(
            3,
            user_id=user.id,
            title='Other title',
            description='other description',
            state=TodoState.todo,
        )
    )

    await session.commit()

    response = client.get(
        f'/todos/?title={title}&description={description[:8]}&state={state.value}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert len(response.json()['todos']) == expected_todos


async def test_patch_todo(
    session: AsyncSession, client: TestClient, user, token
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.patch(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Test'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['title'] == 'Test'


async def test_patch_wrong_user_todo(
    session: AsyncSession, client: TestClient, user, token, other_user
):
    todo_user = TodoFactory(user_id=user.id)
    todo_other_user = TodoFactory(user_id=other_user.id)

    session.add_all([todo_user, todo_other_user])
    await session.commit()

    response = client.patch(
        f'/todos/{other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
        json={'title': 'Test'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_patch_not_found_todo(client: TestClient, token):
    response = client.patch(
        '/todos/42',
        headers={'Authorization': f'Bearer {token}'},
        json={},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_delete_todo(
    session: AsyncSession, client: TestClient, user, token
):
    todo = TodoFactory(user_id=user.id)

    session.add(todo)
    await session.commit()

    response = client.delete(
        f'/todos/{todo.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'message': 'Task has been deleted successfully'}


async def test_delete_wrong_user_todo(
    session: AsyncSession, client: TestClient, user, token, other_user
):
    todo_user = TodoFactory(user_id=user.id)
    todo_other_user = TodoFactory(user_id=other_user.id)

    session.add_all([todo_user, todo_other_user])
    await session.commit()

    response = client.delete(
        f'/todos/{todo_other_user.id}',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_delete_not_found_todo(client: TestClient, token):
    response = client.delete(
        '/todos/42',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert response.json() == {'detail': 'Task not found'}


async def test_list_todos_should_return_all_expected_fields(
    session: AsyncSession, client: TestClient, user, token, mock_db_time
):
    with mock_db_time(model=Todo) as time:
        todo = TodoFactory.create(user_id=user.id)
        session.add(todo)
        await session.commit()

    await session.refresh(todo)
    response = client.get(
        '/todos/',
        headers={'Authorization': f'Bearer {token}'},
    )

    assert response.json()['todos'] == [
        {
            'created_at': time.isoformat(),
            'updated_at': time.isoformat(),
            'description': todo.description,
            'id': todo.id,
            'state': todo.state,
            'title': todo.title,
        }
    ]
