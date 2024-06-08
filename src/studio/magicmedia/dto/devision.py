import random
from enum import Enum


class Division(Enum):
    DEVELOPMENT = "DEVELOPMENT"
    SECURITY = "SECURITY"
    SALES = "SALES"
    OTHER = "OTHER"

    @staticmethod
    def get_random_division() -> str:
        return random.choice(list(Division))  # noqa S311
