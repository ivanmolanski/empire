from fastapi import APIRouter, status
from models import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse, ErrorResponse

router = APIRouter()

@router.post(
    "/register",
    response_model=UserResponse,
    responses={400: {"model": ErrorResponse}},
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user"
)
def register_user(request: UserRegisterRequest):
    """
    Register a new user.
    - **username**: Unique username.
    - **email**: User's email address.
    - **password**: User's password.
    """
    # TODO: Add database logic to create user and hash password.
    return UserResponse(user_id="user_123", username=request.username, email=request.email)

@router.post(
    "/login",
    response_model=LoginResponse,
    responses={401: {"model": ErrorResponse}},
    status_code=status.HTTP_200_OK,
    summary="User login (returns JWT)"
)
def login_user(request: UserLoginRequest):
    """
    Authenticate user and return JWT token.
    - **username**: User's username.
    - **password**: User's password.
    """
    # TODO: Add authentication logic and JWT generation.
    return LoginResponse(access_token="fake-jwt-token", token_type="bearer")
