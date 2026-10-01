import re
from dataclasses import dataclass, asdict
from enum import Enum
from faker import Faker


fake = Faker("en_US")
fake_ru = Faker("ru_RU")


# ---------- Requirements ----------
class Limits:
    USERNAME_MIN, USERNAME_MAX = 3, 15
    PASSWORD_MIN = 8
    PASSWORD_SPECIALS = "!@#$%^&*()_+"
    DEPOSIT_MIN, DEPOSIT_MAX = 1000, 9000
    TRANSFER_MIN, TRANSFER_MAX = 500, 10000
    CREDIT_MIN, CREDIT_MAX = 5000, 15000
    MAX_ACCOUNTS = 2


class Role(str, Enum):
    USER = "ROLE_USER"
    CREDIT_SECRET = "ROLE_CREDIT_SECRET"


class OperationType(str, Enum):
    DEPOSIT = "deposit"
    TRANSFER_IN = "transfer_in"
    TRANSFER_OUT = "transfer_out"


# ---------- Username ----------
class UsernameFactory:
    @staticmethod
    def valid(length: int | None = None) -> str:
        length = length or fake.random_int(Limits.USERNAME_MIN, Limits.USERNAME_MAX)
        base = re.sub(r"[^A-Za-z0-9]", "", fake.unique.user_name())
        base += fake.bothify("?#" * Limits.USERNAME_MAX)
        return base[:length]

    @staticmethod
    def boundary_valid() -> list[str]:
        return [UsernameFactory.valid(n) for n in
                (Limits.USERNAME_MIN, Limits.USERNAME_MIN + 1,
                 Limits.USERNAME_MAX - 1, Limits.USERNAME_MAX)]

    @staticmethod
    def invalid_cases() -> dict[str, str]:
        return {
            "too_short":     UsernameFactory.valid(Limits.USERNAME_MAX)[: Limits.USERNAME_MIN - 1],
            "too_long":      UsernameFactory.valid(Limits.USERNAME_MAX) + "x",
            "special_char":  UsernameFactory.valid(5) + "!",
            "cyrillic":      fake_ru.first_name()[:10],
            "with_space":    "ab cd",
            "empty":         "",
        }


# ---------- Password ----------
class PasswordFactory:
    @staticmethod
    def valid(length: int | None = None) -> str:
        return fake.password(
            length=length or fake.random_int(Limits.PASSWORD_MIN, 20),
            special_chars=True, digits=True, upper_case=True, lower_case=True,
        )

    @staticmethod
    def invalid_cases() -> dict[str, str]:
        p = dict(length=10)
        return {
            "too_short":   fake.password(length=Limits.PASSWORD_MIN - 1),
            "no_upper":    fake.password(**p, upper_case=False),
            "no_lower":    fake.password(**p, lower_case=False),
            "no_digit":    fake.password(**p, digits=False),
            "no_special":  fake.password(**p, special_chars=False),
            "cyrillic":    "Пароль1!аБв",
            "empty":       "",
        }


# ---------- Sums (deposit / transfer / credit) ----------
class AmountFactory:

    def __init__(self, min_: int, max_: int):
        self.min, self.max = min_, max_

    def valid(self) -> int:
        return fake.random_int(self.min, self.max)

    def boundary_valid(self) -> list[int]:
        return [self.min, self.min + 1, self.max - 1, self.max]

    def boundary_invalid(self) -> list[int]:
        return [self.min - 1, self.max + 1]

    def invalid_cases(self) -> dict[str, object]:
        return {"zero": 0, "negative": -self.min, "float": self.min + 0.5,
                "string": str(self.min), "null": None}


Deposit = AmountFactory(Limits.DEPOSIT_MIN, Limits.DEPOSIT_MAX)
Transfer = AmountFactory(Limits.TRANSFER_MIN, Limits.TRANSFER_MAX)
Credit = AmountFactory(Limits.CREDIT_MIN, Limits.CREDIT_MAX)


# ---------- Request model ----------
@dataclass
class CreateUserRequest:
    username: str
    password: str
    role: str

    def to_json(self) -> dict:
        return asdict(self)


class UserFactory:
    @staticmethod
    def build(role: Role = Role.USER, **overrides) -> CreateUserRequest:
        data = dict(username=UsernameFactory.valid(),
                    password=PasswordFactory.valid(),
                    role=role.value)
        data.update(overrides)
        return CreateUserRequest(**data)

    @staticmethod
    def build_batch(n: int, role: Role = Role.USER) -> list[CreateUserRequest]:
        return [UserFactory.build(role) for _ in range(n)]


if __name__ == "__main__":
    print("== Пользователи ==")
    print(UserFactory.build().to_json())
    print(UserFactory.build(Role.CREDIT_SECRET).to_json())
    print("override:", UserFactory.build(username="ab").to_json())

    print("\n== Username: границы / негатив ==")
    print(UsernameFactory.boundary_valid())
    print(UsernameFactory.invalid_cases())

    print("\n== Password: негатив ==")
    print(PasswordFactory.invalid_cases())

    for name, f in (("Deposit", Deposit), ("Transfer", Transfer), ("Credit", Credit)):
        print(f"\n== {name} ==  valid={f.valid()}  "
              f"boundary_ok={f.boundary_valid()}  boundary_bad={f.boundary_invalid()}")