import random
import string

import pycountry


def get_random_country() -> str:
    countries = [country.name for country in pycountry.countries]
    return random.choice(countries)  # noqa S311


def get_random_string(length: int = 10) -> str:
    letters = string.ascii_lowercase
    return "".join(random.choice(letters) for i in range(length))  # noqa S311
