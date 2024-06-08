import random
from enum import Enum


class Division(Enum):
    DEVELOPMENT = "DEVELOPMENT"
    SECURITY = "SECURITY"
    SALES = "SALES"
    OTHER = "OTHER"

    @staticmethod
    def get_random_division() -> int:
        return random.choice(list(Division)).value  # noqa S311
