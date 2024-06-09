import os
import random
import threading
import time
from typing import Any

from dotenv import load_dotenv
from locust import constant, events, task
from pb.rpc_create_vacancy_pb2 import CreateVacancyRequest
from pb.rpc_update_vacancy_pb2 import UpdateVacancyRequest
from pb.vacancy_pb2 import VacancyResponse
from pb.vacancy_service_pb2 import GetVacanciesRequest, VacancyRequest
from pb.vacancy_service_pb2_grpc import VacancyServiceStub
from studio.magicmedia.common.grpc_user import GrpcUser
from studio.magicmedia.dto import Division
from studio.magicmedia.utils.utils import get_random_country, get_random_string

# Load environment variables from .env file
load_dotenv()


class VacancyGrpcUser(GrpcUser):
    host = (
        f"{os.getenv('SERVICE_HOST', 'localhost')}:{os.getenv('SERVICE_PORT', '7823')}"
    )
    stub_class = VacancyServiceStub
    wait_time = constant(30)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.background_task_interval = 45
        self.stop_background_task_flag = threading.Event()
        self.background_thread = threading.Thread(target=self.run_background_task)
        self.background_thread.daemon = True
        self.background_thread.start()

        # Stop the background thread when the test stops
        events.quitting.add_listener(self.stop_background_task)

    @task
    def create_get_update_delete_vacancy(self) -> None:
        create_response: VacancyResponse = self.stub.CreateVacancy(
            CreateVacancyRequest(
                Title=get_random_string(),
                Description=get_random_string(),
                Division=Division.get_random_division(),  # noqa S311
                Country=get_random_country(),  # noqa S311
            )
        )
        vacancy_id = create_response.vacancy.Id

        self.stub.UpdateVacancy(
            UpdateVacancyRequest(
                Id=vacancy_id,
                Title=get_random_string(),
                Description=get_random_string(),
                Views=random.randint(1, 1000),  # noqa S311
                Division=Division.get_random_division(),  # noqa S311
                Country=get_random_country(),  # noqa S311
            )
        )

        self.stub.GetVacancy(VacancyRequest(Id=vacancy_id))
        self.stub.DeleteVacancy(VacancyRequest(Id=vacancy_id))

    def fetch_all_vacancies(self) -> None:
        self.stub.GetVacancies(
            GetVacanciesRequest(
                page=random.randint(1, 10), limit=random.randint(1, 100)  # noqa S311
            )
        )

    def run_background_task(self) -> None:
        while not self.stop_background_task_flag.is_set():
            self.fetch_all_vacancies()
            time.sleep(self.background_task_interval)

    def stop_background_task(self) -> None:
        # This will trigger stopping the background thread
        self.stop_background_task_flag.set()
        if self.background_thread.is_alive():
            self.background_thread.join(timeout=1)
