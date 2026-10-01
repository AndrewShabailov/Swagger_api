import pytest

from src.main.api.data.factories import UserFactory, UsernameFactory, PasswordFactory, Role


class TestCreateUser:

    @pytest.mark.parametrize("role", list(Role), ids=lambda role: role.value)
    def test_create_user(self, create_user, role):
        user = UserFactory.build(role)

        r = create_user(user)

        assert r.status_code == 200, r.text
        assert r.json()["username"] == user.username

    @pytest.mark.parametrize("username", UsernameFactory.boundary_valid(),
                             ids=lambda name: f"len_{len(name)}")
    def test_create_user_username_boundary(self, create_user, username):
        r = create_user(UserFactory.build(username=username))

        assert r.status_code == 200, r.text

    @pytest.mark.parametrize("case, username", UsernameFactory.invalid_cases().items(),
                             ids=UsernameFactory.invalid_cases().keys())
    def test_create_user_invalid_username(self, create_user, case, username):
        r = create_user(UserFactory.build(username=username))

        assert r.status_code == 400, f"{case}: {r.status_code} {r.text}"

    @pytest.mark.parametrize("case, password", PasswordFactory.invalid_cases().items(),
                             ids=PasswordFactory.invalid_cases().keys())
    def test_create_user_invalid_password(self, create_user, case, password):
        r = create_user(UserFactory.build(password=password))

        assert r.status_code == 400, f"{case}: {r.status_code} {r.text}"

    def test_create_duplicate_user(self, create_user):
        user = UserFactory.build()
        assert create_user(user).status_code == 200

        r = create_user(user)

        assert r.status_code == 409, r.text

    @pytest.mark.xfail(strict=True,
                       reason="BUG: на дубликат username сервер возвращает ошибку "
                              "про лимит банковских счетов")
    def test_create_duplicate_user_error_message(self, create_user):
        user = UserFactory.build()
        assert create_user(user).status_code == 200

        r = create_user(user)

        assert "accounts" not in r.json().get("error", ""), r.text

    def test_create_user_without_token(self, create_user, anonymous_client):
        r = create_user(UserFactory.build(), client=anonymous_client)

        assert r.status_code == 401, r.text
