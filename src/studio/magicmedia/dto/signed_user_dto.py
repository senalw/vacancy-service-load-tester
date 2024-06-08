from dataclasses import dataclass


@dataclass()
class SignedUser:
    email: str
    access_token: str
    refresh_token: str
