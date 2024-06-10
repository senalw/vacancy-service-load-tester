from typing import Any, List, Type

import grpc
from locust import User
from locust.exception import LocustError
from studio.magicmedia.common.locust_interceptor import LocustInterceptor


class GrpcUser(User):
    abstract = True
    stub_classes: List[Type] = []

    def __init__(self, environment: Any) -> None:
        super().__init__(environment)
        if not self.host:
            raise LocustError("You must specify the host.")
        if not self.stub_classes:
            raise LocustError("You must specify at least one stub_class.")

        self._channel = grpc.insecure_channel(self.host)
        interceptor = LocustInterceptor(environment=environment)
        self._channel = grpc.intercept_channel(self._channel, interceptor)

        self.stubs = {
            stub_class: stub_class(self._channel) for stub_class in self.stub_classes
        }
