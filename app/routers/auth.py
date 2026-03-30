from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordBearer

from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse
from app.schemas.user import UserResponse
from app.services import auth as auth_service

router = APIRouter(prefix="/api/auth", tags=["auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(data: RegisterRequest):
    user = await auth_service.register_user(data.email, data.password, data.full_name)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(data: LoginRequest):
    return await auth_service.login_user(data.email, data.password)


@router.get("/me", response_model=UserResponse)
async def get_me(token: str = Depends(oauth2_scheme)):
    return await auth_service.get_user_from_token(token)
