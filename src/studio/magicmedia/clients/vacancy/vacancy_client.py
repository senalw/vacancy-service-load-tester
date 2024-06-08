import grpc
from studio.magicmedia.api.v1.rpc_create_vacancy_pb2 import CreateVacancyRequest
from studio.magicmedia.api.v1.rpc_update_vacancy_pb2 import UpdateVacancyRequest
from studio.magicmedia.api.v1.vacancy_pb2 import Vacancy
from studio.magicmedia.api.v1.vacancy_pb2 import VacancyResponse
from studio.magicmedia.api.v1.vacancy_service_pb2 import DeleteVacancyResponse
from studio.magicmedia.api.v1.vacancy_service_pb2 import GetVacanciesRequest
from studio.magicmedia.api.v1.vacancy_service_pb2 import VacancyRequest
from studio.magicmedia.api.v1.vacancy_service_pb2_grpc import VacancyServiceStub


class VacancyClient:
    def __init__(self, address: str = "vacancies.cyrextech.net:7823") -> None:
        self.channel = grpc.insecure_channel(address)
        self.stub = VacancyServiceStub(self.channel)

    def create_vacancy(
        self, title: str, description: str, division: str, country: str
    ) -> VacancyResponse:
        request = CreateVacancyRequest(
            Title=title, Description=description, Division=division, Country=country
        )
        response = self.stub.CreateVacancy(request)
        return response

    def get_vacancy(self, id: str) -> VacancyResponse:
        request = VacancyRequest(Id=id)
        response = self.stub.GetVacancy(request)
        return response

    def get_vacancies(self, page: int = 1, limit: int = 10) -> Vacancy:
        request = GetVacanciesRequest(page=page, limit=limit)
        response = self.stub.GetVacancies(request)
        return response

    def update_vacancy(
        self,
        id: str,
        title: str,
        description: str,
        views: int,
        division: str,
        country: str,
    ) -> VacancyResponse:
        request = UpdateVacancyRequest(
            Id=id,
            Title=title,
            Description=description,
            Views=views,
            Division=division,
            Country=country,
        )
        response = self.stub.UpdateVacancy(request)
        return response

    def delete_vacancy(self, id: str) -> DeleteVacancyResponse:
        request = VacancyRequest(Id=id)
        response = self.stub.DeleteVacancy(request)
        return response
