from typing import Any, Callable

from grpc import (
    ClientCallDetails,
    UnaryStreamClientInterceptor,
    UnaryUnaryClientInterceptor,
)


class AuthInterceptor(UnaryUnaryClientInterceptor, UnaryStreamClientInterceptor):
    def __init__(self, access_token: str) -> None:
        self.access_token = access_token

    def intercept_unary_unary(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> Callable:
        """
        Intercept one request, one response rpc calls.
        """
        client_call_details = self._add_token_metadata(client_call_details)
        return continuation(client_call_details, request)

    def intercept_unary_stream(
        self,
        continuation: Callable,
        client_call_details: ClientCallDetails,
        request: Any,
    ) -> Callable:
        """
        Intercept one request and mult-response rpc calls
        """
        client_call_details = self._add_token_metadata(client_call_details)
        return continuation(client_call_details, request)

    def _add_token_metadata(
        self, client_call_details: ClientCallDetails
    ) -> ClientCallDetails:
        new_metadata = client_call_details.metadata or ()
        new_metadata = new_metadata + (
            ("authorization", f"Bearer {self.access_token}"),
        )
        return client_call_details._replace(metadata=new_metadata)
