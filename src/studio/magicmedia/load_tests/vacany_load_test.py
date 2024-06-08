import random
import string
from configparser import ConfigParser
from typing import Any, List

import pycountry
from locust import between, HttpUser, task
from pb.rpc_signin_user_pb2 import SignInUserResponse
from pb.vacancy_pb2 import VacancyResponse
from settings import ROOT_DIR
from studio.magicmedia.clients import AuthClient, VacancyClient
from studio.magicmedia.config import Config
from studio.magicmedia.dto.devision import Division
from studio.magicmedia.dto.signed_user_dto import SignedUser
from studio.magicmedia.load_tests.utils import schedule_task


class VacancyUser(HttpUser):
    wait_time = between(1, 2)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        config_parser: ConfigParser = ConfigParser()
        config_parser.read(f"{ROOT_DIR}/resources/config.ini")
        config: Config = Config(config_parser)
        user_config: Config.UserConfig = config.user_config
        self.user_credentials = {
            user_config.user_1_email: user_config.user_1_password,
            user_config.user_2_email: user_config.user_2_password,
            user_config.user_3_email: user_config.user_3_password,
        }
        self.auth_client: AuthClient = AuthClient()
        self.vacancy_client: VacancyClient = VacancyClient()
        self.countries = [country.name for country in pycountry.countries]
        self.signed_users: List[SignedUser] = []
        self.user_email = None
        self.access_token = None

    @staticmethod
    def random_string(length: int = 10) -> str:
        letters = string.ascii_lowercase
        return "".join(random.choice(letters) for i in range(length))  # noqa S311

    def on_start(self) -> None:
        # Sign-in users
        for email in list(self.user_credentials.keys()):
            response: SignInUserResponse = self.auth_client.sign_in_user(
                email, self.user_credentials[email]
            )
            if response.status == "success":
                user: SignedUser = SignedUser(
                    email=email,
                    access_token=response.access_token,
                    refresh_token=response.refresh_token,
                )
                self.signed_users.append(user)

        # Select a random user credential for this instance
        selected_user = random.choice(self.signed_users)  # noqa S311
        self.user_email = selected_user.email
        self.access_token = selected_user.access_token

        # Schedule the recurring task
        schedule_task(self.create_get_update_delete_vacancy, interval=30)
        schedule_task(self.fetch_all_vacancies, interval=45)

    @task
    def create_get_update_delete_vacancy(self) -> None:
        create_response: VacancyResponse = self.vacancy_client.create_vacancy(
            title=self.random_string(),
            description=self.random_string(),
            division=Division.get_random_division(),  # noqa S311
            country=random.choice(self.countries),  # noqa S311
        )

        vacancy_id = create_response.vacancy.Id
        self.vacancy_client.update_vacancy(
            id=vacancy_id,
            title=self.random_string(),
            description=self.random_string(),
            views=random.randint(1, 1000),  # noqa S311
            division=random.choice(self.countries),  # noqa S311
            country=random.choice(self.countries),  # noqa S311
        )
        self.vacancy_client.get_vacancy(vacancy_id)
        self.vacancy_client.delete_vacancy(vacancy_id)

    @task
    def fetch_all_vacancies(self) -> None:
        self.client.fetch_all_vacancies()
