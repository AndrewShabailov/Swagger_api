import pytest
import requests

from src.main.api.data.factories import UserFactory, UsernameFactory, PasswordFactory, Role
from src.main.api.data.config import BASE_URL

CREATE_URL = f"{BASE_URL}/admin/create"


class TestCreateUser:

    @pytest.mark.parametrize("role", [Role.USER, Role.CREDIT_SECRET])
    def test_create_user(self, admin_headers, role):
        user = UserFactory.build(role)

        r = requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers)

        assert r.status_code == 200, r.text
        assert r.json()["username"] == user.username


    @pytest.mark.parametrize("username", UsernameFactory.boundary_valid())
    def test_create_user_username_boundary(self, admin_headers, username):
        user = UserFactory.build(username=username)

        r = requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers)

        assert r.status_code == 200, r.text


    @pytest.mark.parametrize("case, username",
                             UsernameFactory.invalid_cases().items(),
                             ids=UsernameFactory.invalid_cases().keys())
    def test_create_user_invalid_username(self, admin_headers, case, username):
        user = UserFactory.build(username=username)

        r = requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers)

        assert r.status_code == 400, f"{case}: {r.status_code} {r.text}"


    @pytest.mark.parametrize("case, password",
                             PasswordFactory.invalid_cases().items(),
                             ids=PasswordFactory.invalid_cases().keys())
    def test_create_user_invalid_password(self, admin_headers, case, password):
        user = UserFactory.build(password=password)

        r = requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers)

        assert r.status_code == 400, f"{case}: {r.status_code} {r.text}"


    def test_create_duplicate_user(self, admin_headers):
        user = UserFactory.build()
        assert requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers).status_code == 200

        r = requests.post(CREATE_URL, json=user.to_json(), headers=admin_headers)

        assert r.status_code == 409, r.text
        assert "User already has maximum number of accounts(2)" in r.json()["error"]


    def test_create_user_without_token(self):
        r = requests.post(CREATE_URL, json=UserFactory.build().to_json())
        assert r.status_code == 401