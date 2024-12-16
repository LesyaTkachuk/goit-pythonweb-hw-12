from unittest.mock import Mock
import pytest
from src.conf import messages
from sqlalchemy import select

from src.database.models import Contact
from tests.conftest import TestingSessionLocal

contact_data = {
    "name": "Test contact",
    "surname": "Test surname",
    "email": "test@test.com",
    "phone_number": "+38099238238",
    "birthday": "2000-01-01",
    "groups": [],
    "is_active": True,
}
updated_contact_data = {
    "name": "Updated contact",
    "surname": "Updated surname",
    "email": "updated_test@test.com",
    "phone_number": "+38099238238",
    "birthday": "2000-01-01",
    "groups": [],
    "is_active": True,
}


def test_create_contact(client, get_access_token):
    response = client.post(
        "/api/contacts",
        json=contact_data,
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 201, response.text
    data = response.json()
    assert data["name"] == "Test contact"
    assert data["surname"] == "Test surname"
    assert data["email"] == "test@test.com"
    assert "id" in data


def test_get_contact_by_id(client, get_access_token):
    response = client.get(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Test contact"
    assert "id" in data


def test_get_contact_not_found(client, get_access_token):
    response = client.get(
        "/api/contacts/2", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_get_contacts(client, get_access_token):
    response = client.get(
        "/api/contacts", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert isinstance(data, list)
    assert data[0]["name"] == "Test contact"
    assert "id" in data[0]


def test_update_contact(client, get_access_token):
    response = client.put(
        "/api/contacts/1",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] != "Test contact"
    assert data["name"] == "Updated contact"
    assert data["email"] == "updated_test@test.com"
    assert "id" in data


def test_update_contact_unprodessable(client, get_access_token):
    response = client.put(
        "/api/contacts/1",
        json={"name": "new_test_contact"},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 422, response.text


def test_update_contact_not_found(client, get_access_token):
    response = client.put(
        "/api/contacts/2",
        json=updated_contact_data,
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND


def test_update_contact_is_active(client, get_access_token):
    response = client.patch(
        "/api/contacts/1",
        json={"is_active": False},
        headers={"Authorization": f"Bearer {get_access_token}"},
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["is_active"] == False


def test_delete_contact(client, get_access_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["name"] == "Updated contact"
    assert "id" in data


def test_delete_contact_not_found(client, get_access_token):
    response = client.delete(
        "/api/contacts/1", headers={"Authorization": f"Bearer {get_access_token}"}
    )
    assert response.status_code == 404, response.text
    data = response.json()
    assert data["detail"] == messages.CONTACT_NOT_FOUND
