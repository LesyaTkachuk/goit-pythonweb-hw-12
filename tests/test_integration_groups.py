from src.conf import messages
from sqlalchemy import select

from src.database.models import Group
from tests.conftest import TestingSessionLocal

group_data = {"name": "Test Group"}


def test_create_group(client, get_access_token):
    response = client.post(
        "/api/groups",
        json=group_data,
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test Group"
    assert "id" in data


def test_get_group_by_id(client, get_access_token):
    response = client.get(
        "/api/groups/1", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test Group"
    assert "id" in data


def test_get_group_not_found(client, get_access_token):
    response = client.get(
        "/api/groups/2", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.GROUP_NOT_FOUND


def test_get_groups(client, get_access_token):
    response = client.get(
        "/api/groups", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Test Group"
    assert "id" in data[0]


def test_update_group(client, get_access_token):
    response = client.put(
        "/api/groups/1",
        json={"name": "new_test_group"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "new_test_group"
    assert "id" in data


def test_update_group_not_found(client, get_access_token):
    response = client.put(
        "/api/groups/2",
        json={"name": "new_test_group"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.GROUP_NOT_FOUND


def test_delete_group(client, get_access_token):
    response = client.delete(
        "/api/groups/1", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 204, response.text


