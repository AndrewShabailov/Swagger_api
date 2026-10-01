import requests

from src.main.api.clients.base_client import BaseClient
from src.main.api.clients.endpoints import Endpoints
from src.main.api.models.request_models import BaseRequest


class AdminClient(BaseClient):

    def create_user(self, user: BaseRequest | dict) -> requests.Response:
        body = user.to_json() if isinstance(user, BaseRequest) else user
        return self.post(Endpoints.ADMIN_CREATE_USER, json=body)

    def delete_user(self, user_id: int | str) -> requests.Response:
        return self.delete(Endpoints.ADMIN_DELETE_USER.format(user_id=user_id))
