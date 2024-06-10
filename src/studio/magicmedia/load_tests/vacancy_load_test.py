import os
import random
import threading
import time
from typing import Any

from dotenv import load_dotenv
from locust import constant, events, task
from pb.auth_service_pb2_grpc import AuthServiceStub
from pb.rpc_create_vacancy_pb2 import CreateVacancyRequest
from pb.rpc_signin_user_pb2 import SignInUserInput, SignInUserResponse
from pb.rpc_update_vacancy_pb2 import UpdateVacancyRequest
from pb.vacancy_pb2 import VacancyResponse
from pb.vacancy_service_pb2 import GetVacanciesRequest, VacancyRequest
from pb.vacancy_service_pb2_grpc import VacancyServiceStub
from studio.magicmedia.common.grpc_user import GrpcUser
from studio.magicmedia.dto import Division
from studio.magicmedia.utils.utils import (
    get_random_country,
    get_random_string,
)

# Load environment variables from .env file
load_dotenv()


class VacancyGrpcUser(GrpcUser):
    host = (
        f"{os.getenv('SERVICE_HOST', 'localhost')}:{os.getenv('SERVICE_PORT', '7823')}"
    )
    stub_classes = [AuthServiceStub, VacancyServiceStub]
    wait_time = constant(30)
    user_index = 0

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.user_credentials = {
            os.getenv("USER_1_EMAIL"): os.getenv("USER_1_PASSWORD"),
            os.getenv("USER_2_EMAIL"): os.getenv("USER_2_PASSWORD"),
            os.getenv("USER_3_EMAIL"): os.getenv("USER_3_PASSWORD"),
        }
        self.background_task_interval = 45
        self.stop_background_task_flag = threading.Event()
        self.background_thread = threading.Thread(target=self.run_background_task)
        self.background_thread.daemon = True
        self.background_thread.start()

        # Stop the background thread when the test stops
        events.quitting.add_listener(self.stop_background_task)

    def on_start(self) -> None:
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

    @task
    def create_get_update_delete_vacancy(self) -> None:
        stub = self.stubs[VacancyServiceStub]
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

    def list_all_vacancies(self) -> None:
        stub = self.stubs[VacancyServiceStub]
        stub.GetVacancies(
            GetVacanciesRequest(
                page=random.randint(1, 10), limit=random.randint(1, 100)  # noqa S311
            )
        )

    def run_background_task(self) -> None:
        while not self.stop_background_task_flag.is_set():
            self.list_all_vacancies()
            time.sleep(self.background_task_interval)

    def stop_background_task(self, **kwargs: Any) -> None:
        # This will trigger stopping the background thread
        self.stop_background_task_flag.set()
        if self.background_thread.is_alive():
            self.background_thread.join(timeout=1)
