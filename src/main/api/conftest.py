import pytest
import requests
from src.main.api.data.config import BASE_URL, ADMIN_CREDS

CREATE_URL = f"{BASE_URL}/admin/create"
DELETE_URL = f"{BASE_URL}/admin/users/{{user_id}}"


@pytest.fixture(scope="session")
def admin_token() -> str:
    r = requests.post(f"{BASE_URL}/auth/token/login", json=ADMIN_CREDS)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture
def admin_headers(admin_token) -> dict:
    return {"Authorization": f"Bearer {admin_token}"}


@pytest.fixture
def create_user(admin_headers):
    created_ids = []

    def _create(body: dict, headers: dict | None = None) -> requests.Response:
        r = requests.post(CREATE_URL, json=body,
                          headers=admin_headers if headers is None else headers)
        if r.status_code == 200:
            created_ids.append(r.json()["id"])
        return r

    yield _create

    errors = []                               # teardown
    for user_id in created_ids:
        r = requests.delete(DELETE_URL.format(user_id=user_id), headers=admin_headers)
        if r.status_code not in (200, 204):
            errors.append(f"{user_id}: {r.status_code} {r.text}")
    assert not errors, f"Не удалось удалить: {errors}"
