import requests

from src.main.api.clients.base_client import BaseClient
from src.main.api.clients.endpoints import Endpoints


class AuthClient(BaseClient):

    def login(self, username: str, password: str) -> requests.Response:
        return self.post(Endpoints.LOGIN, json={"username": username, "password": password})
