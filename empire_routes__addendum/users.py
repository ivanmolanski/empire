from fastapi import APIRouter, HTTPException
from models import UserRegisterRequest, UserLoginRequest, UserResponse, LoginResponse

router = APIRouter()

@router.post("/register", response_model=UserResponse, status_code=201)
def register_user(user: UserRegisterRequest):
    # TODO: Add DB logic here
    return UserResponse(user_id="user_123", username=user.username, email=user.email)

@router.post("/login", response_model=LoginResponse)
def login_user(credentials: UserLoginRequest):
    # TODO: Validate user, return JWT
    if credentials.username != "admin":
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return LoginResponse(access_token="dummy.jwt.token", token_type="bearer")