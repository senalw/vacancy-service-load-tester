import grpc
from src.studio.magicmedia.api.v1.auth_service_pb2 import VerifyEmailRequest
from src.studio.magicmedia.api.v1.auth_service_pb2_grpc import AuthServiceStub
from src.studio.magicmedia.api.v1.rpc_signin_user_pb2 import SignInUserInput
from src.studio.magicmedia.api.v1.rpc_signin_user_pb2 import SignInUserResponse
from src.studio.magicmedia.api.v1.rpc_signup_user_pb2 import SignUpUserInput
from src.studio.magicmedia.api.v1.rpc_signup_user_pb2 import SignUpUserResponse
from src.studio.magicmedia.api.v1.user_pb2 import GenericResponse


class AuthClient:
    def __init__(self, address: str = "vacancies.cyrextech.net:7823") -> None:
        self.channel = grpc.insecure_channel(address)
        self.stub = AuthServiceStub(self.channel)

    def sign_up_user(self, name: str, email: str, password: str) -> SignUpUserResponse:
        request = SignUpUserInput(
            name=name, email=email, password=password, passwordConfirm=password
        )
        response = self.stub.SignUpUser(request)
        return response

    def verify_email(self, verification_code: str) -> GenericResponse:
        request = VerifyEmailRequest(verificationCode=verification_code)
        response = self.stub.VerifyEmail(request)
        return response

    def sign_in_user(self, email: str, password: str) -> SignInUserResponse:
        request = SignInUserInput(email=email, password=password)
        response = self.stub.SignInUser(request)
        return response
