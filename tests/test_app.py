import pytest


def test_new_app_user(test_client):
    response = test_client.post(
        "/user",
        json = {
            "email": "pytest@example.com",
            "password": "testing"
            }
        )
    assert response.status_code == 201

