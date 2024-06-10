import os
import random
import time
from typing import Any

from dotenv import load_dotenv
from locust import task, TaskSet, User
from pb.auth_service_pb2_grpc import AuthServiceStub
from pb.rpc_create_vacancy_pb2 import CreateVacancyRequest
from pb.rpc_signin_user_pb2 import SignInUserInput, SignInUserResponse
from pb.rpc_update_vacancy_pb2 import UpdateVacancyRequest
from pb.vacancy_pb2 import VacancyResponse
from pb.vacancy_service_pb2 import GetVacanciesRequest, VacancyRequest
from pb.vacancy_service_pb2_grpc import VacancyServiceStub
from studio.magicmedia.common.grpc_user import GrpcUser
from studio.magicmedia.dto import Division
from studio.magicmedia.utils.utils import get_random_country, get_random_string

# Load environment variables from .env file
load_dotenv()


class VacancyTasks(TaskSet):
    def __init__(self, parent: User) -> None:
        super().__init__(parent)
        self.fetch_vacancies_timer = None
        self.create_vacancy_timer = None

    def on_start(self) -> None:
        self.user.login_round_robin()
        self.create_vacancy_timer = time.time()
        self.fetch_vacancies_timer = time.time()

    @task
    def create_get_update_delete_vacancy(self) -> None:
        # run in 30s intervals
        if time.time() - self.create_vacancy_timer >= 30:
            stub = self.user.stubs[VacancyServiceStub]
            create_response: VacancyResponse = stub.CreateVacancy(
                CreateVacancyRequest(
                    Title=get_random_string(),
                    Description=get_random_string(),
                    Division=Division.get_random_division(),  # noqa S311
                    Country=get_random_country(),  # noqa S311
                )
            )
            vacancy_id = create_response.vacancy.Id

            stub.UpdateVacancy(
                UpdateVacancyRequest(
                    Id=vacancy_id,
                    Title=get_random_string(),
                    Description=get_random_string(),
                    Views=random.randint(1, 1000),  # noqa S311
                    Division=Division.get_random_division(),  # noqa S311
                    Country=get_random_country(),  # noqa S311
                )
            )

            stub.GetVacancy(VacancyRequest(Id=vacancy_id))
            stub.DeleteVacancy(VacancyRequest(Id=vacancy_id))
            self.create_vacancy_timer = time.time()  # Reset the timer

    @task
    def list_all_vacancies(self) -> None:
        # run in
        if time.time() - self.fetch_vacancies_timer >= 45:
            stub = self.user.stubs[VacancyServiceStub]
            stub.GetVacancies(
                GetVacanciesRequest(
                    page=random.randint(1, 10),  # noqa S311
                    limit=random.randint(1, 100),  # noqa S311
                )
            )
            self.fetch_vacancies_timer = time.time()  # Reset the timer


class VacancyGrpcUser(GrpcUser):
    host = (
        f"{os.getenv('SERVICE_HOST', 'localhost')}:{os.getenv('SERVICE_PORT', '7823')}"
    )
    stub_classes = [AuthServiceStub, VacancyServiceStub]
    tasks = [VacancyTasks]

    user_index = (
        0  # Keep track of the current user index for round-robbin user selection
    )

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_credentials = {
            os.getenv("USER_1_EMAIL"): os.getenv("USER_1_PASSWORD"),
            os.getenv("USER_2_EMAIL"): os.getenv("USER_2_PASSWORD"),
            os.getenv("USER_3_EMAIL"): os.getenv("USER_3_PASSWORD"),
        }

    def login_round_robin(self) -> None:
        stub = self.stubs[AuthServiceStub]
        emails = list(self.user_credentials.keys())

        # Get the current user's email
        email = emails[VacancyGrpcUser.user_index % len(emails)]

        # Update the user index for the next user
        VacancyGrpcUser.user_index += 1

        response: SignInUserResponse = stub.SignInUser(
            SignInUserInput(email=email, password=self.user_credentials[email])
        )
        if response.status == "success":
            print(f"User {email} logged in successfully")
        else:
            raise Exception(f"Failed to log in user {email}: {response.status}")
