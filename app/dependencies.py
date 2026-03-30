from dataclasses import dataclass

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from supabase_auth.errors import AuthApiError

from app.supabase_client import supabase

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


@dataclass
class CurrentUser:
    id: str
    email: str


async def get_current_user(
    token: str = Depends(oauth2_scheme),
) -> CurrentUser:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        response = supabase.auth.get_user(token)
    except AuthApiError:
        raise credentials_exception

    user = response.user
    if user is None:
        raise credentials_exception

    return CurrentUser(id=str(user.id), email=user.email or "")
