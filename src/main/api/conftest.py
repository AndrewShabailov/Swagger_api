import warnings

import pytest

from src.main.api.clients.admin_client import AdminClient
from src.main.api.clients.auth_client import AuthClient
from src.main.api.data.config import ADMIN_CREDS


@pytest.fixture(scope="session")
def admin_token() -> str:
    """Логинимся админом один раз на всю сессию."""
    r = AuthClient().login(**ADMIN_CREDS)
    assert r.status_code == 200, r.text
    return r.json()["token"]


@pytest.fixture(scope="session")
def admin_client(admin_token) -> AdminClient:
    return AdminClient(token=admin_token)


@pytest.fixture
def anonymous_client() -> AdminClient:
    """Клиент без токена — для проверок авторизации."""
    return AdminClient()


@pytest.fixture
def create_user(admin_client):
    """Создаёт пользователей через API и удаляет их после теста.
    Удаляются только реально созданные (ответ 200), даже если тест упал."""
    created_ids = []

    def _create(user, client: AdminClient | None = None):
        r = (client or admin_client).create_user(user)
        if r.status_code == 200:
            user_id = r.json().get("id")
            if user_id is None:
                warnings.warn(f"В ответе на создание нет поля id, удалить не получится: {r.text}")
            else:
                created_ids.append(user_id)
        return r

    yield _create

    errors = []
    for user_id in created_ids:
        r = admin_client.delete_user(user_id)
        if r.status_code not in (200, 204):
            errors.append(f"{user_id}: {r.status_code} {r.text}")
    assert not errors, f"Не удалось удалить пользователей: {errors}"
