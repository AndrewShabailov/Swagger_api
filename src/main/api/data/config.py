import os

BASE_URL = os.getenv("BASE_URL") or "http://localhost:4111/api"

ADMIN_CREDS = {
    "username": os.getenv("ADMIN_USERNAME") or "admin",
    "password": os.getenv("ADMIN_PASSWORD") or "123456",
}