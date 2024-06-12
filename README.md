# vacancy-service-load-tester

## Overview

This assignment covers below scenarios in-terms of load testing Cyrextech gRPC API.

1. Every locust user should login with one of the user credentials created in pre-requirements.
2. In a recurring flow every locust user should execute the following actions every 30 seconds:
   * Create a vacancy with pseudo-random data
   * Update one or more fields in that vacancy
   * Fetch that specific vacancy
   * Delete the vacancy

3. In the background the locust user should fetch a list of all vacancies available on the server
every 45 seconds.

## Approach

1. Use `on_start()` method to login with one of user credentials stored in `.env`[here](.env). 
This method will be invoked for each locust user. 

E.g.
```python
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
```
2. Use locust task to load test `create, get, update, delete` in vacancy gRPC endpoints every 30s intervals. 

E.g.
```python
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
```

3.Use locust task to load test `list_all_vacancies` in vacancy gRPC endpoint every 45s intervals.

E.g.
```python
 def list_all_vacancies(self) -> None:
     stub = self.stubs[VacancyServiceStub]
     stub.GetVacancies(
         GetVacanciesRequest(
             page=random.randint(1, 10), limit=random.randint(1, 100)  # noqa S311
         )
     )
```

## How to setup project
1. Run `make setup` command to install required libraries and generate protocol buffer code. 
2. Run `make setup-style` command to set up python linter.

## How to run load tests
**1. Use locust Web UI to start and monitor tests interactively.**
   1. Go to the project home
   2. Export `PYTHONPATH` as below,
   ```shell
    export PYTHONPATH=$(pwd)/src 
   ```
   3. Run load test by passing locust test file.
   ```shell
   locust -f src/studio/magicmedia/load_tests/vacancy_load_test.py
   ```
   4. Set user count and test running period in locust UI and then start the tests.
   ![configure-parameters-ui.png](resources%2Fstatic%2Fconfigure-parameters-ui.png)
   
   5. You can download the test report from UI from the **DOWNLOAD DATA** tab, once the tests are completed.
   ![download-report.png](resources%2Fstatic%2Fdownload-report.png)
   

**2. Use locust CLI to run tests in headless mode.**
   1. Go to the project home
   2. Export `PYTHONPATH` as below,
   ```shell
   export PYTHONPATH=$(pwd)/src 
   ```
   3. Run locust tests in headless mode. (Without UI)
   ```shell
   locust --headless --users 20 --spawn-rate 2 -H vacancies.cyrextech.net:7823 --run-time 1m -f src/studio/magicmedia/load_tests/vacancy_load_test.py --html=vacancy_load_tests.html
   ```
   
   4. In the above command, set report path after the `--html` parameter.

## Assumptions
1. I decided to use the threading module to run `list_all_vacancies` to avoid waiting for the `create_get_update_delete_vacancy` Locust task to complete, as Locust runs tasks sequentially. 
Now, it is possible to run `list_all_vacancies` at 45s intervals precisely while `create_get_update_delete_vacancy` running in constant 30s intervals.

## Issues Noticed
1. Even though the `SignInUser` endpoint returns an access token and refresh token as the response, 
the gRPC server has not been implemented with an interceptor to check authentication before passing the request to the domain layer.

   E.g. The expectation is for vacancy service RPC calls to fail if a valid token is not present.