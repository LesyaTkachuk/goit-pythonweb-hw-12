from unittest.mock import Mock
import pytest
from src.conf import messages
from sqlalchemy import select

from src.database.models import User
from tests.conftest import TestingSessionLocal

def test_helthcheck(client):
    response = client.get(
        "/api/healthchecker"
    )
    assert response.status_code == 200, response.text
    data = response.json()
    assert data["message"] == "Welcome to FastAPI!"
