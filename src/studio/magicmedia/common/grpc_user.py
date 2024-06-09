"""
Reference: https://docs.locust.io/en/stable/testing-other-systems.html#grpc
"""
from typing import Any

import grpc
from locust import User
from locust.exception import LocustError
from studio.magicmedia.common.locust_interceptor import LocustInterceptor


class GrpcUser(User):
    abstract = True
    stub_class = None

    def __init__(self, environment: Any) -> None:
        super().__init__(environment)
        for attr_value, attr_name in (
            (self.host, "host"),
            (self.stub_class, "stub_class"),
        ):
            if attr_value is None:
                raise LocustError(f"You must specify the {attr_name}.")

        self._channel = grpc.insecure_channel(self.host)
        interceptor = LocustInterceptor(environment=environment)
        self._channel = grpc.intercept_channel(self._channel, interceptor)

        self.stub = self.stub_class(self._channel)
