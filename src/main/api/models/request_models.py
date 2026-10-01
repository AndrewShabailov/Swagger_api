from dataclasses import dataclass, asdict


class BaseRequest:
    def to_json(self) -> dict:
        return asdict(self)


@dataclass
class CreateUserRequest(BaseRequest):
    username: str
    password: str
    role: str
