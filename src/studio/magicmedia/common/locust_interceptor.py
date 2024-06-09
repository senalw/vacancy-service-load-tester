"""
Reference: https://docs.locust.io/en/stable/testing-other-systems.html#grpc
"""
import time
from typing import Any, Callable

import grpc
import grpc.experimental.gevent as grpc_gevent
from grpc_interceptor import ClientInterceptor

# patch grpc so that it uses gevent instead of asyncio
grpc_gevent.init_gevent()


class LocustInterceptor(ClientInterceptor):
    def __init__(self, environment: Any, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.env = environment

    def intercept(
        self,
        method: Callable,
        request_or_iterator: Any,
        call_details: grpc.ClientCallDetails,
    ) -> Any:
        response = None
        exception = None
        start_perf_counter = time.perf_counter()
        response_length = 0
        try:
            response = method(request_or_iterator, call_details)
            if hasattr(
                response, "__iter__"
            ):  # Check if response is an iterator (stream)
                response_length = 0
                for item in response:
                    response_length += item.ByteSize()
            else:
                response_length = response.result().ByteSize() if response else 0
        except grpc.RpcError as e:
            exception = e

        self.env.events.request.fire(
            request_type="grpc",
            name=call_details.method,
            response_time=(time.perf_counter() - start_perf_counter) * 1000,
            response_length=response_length,
            response=response,
            context=None,
            exception=exception,
        )
        return response
