from studio.magicmedia.clients.auth import AuthClient
from studio.magicmedia.clients.vacancy import VacancyClient

if __name__ == "__main__":
    auth_client: AuthClient = AuthClient()
    vacancy_client: VacancyClient = VacancyClient()
