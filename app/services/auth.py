from fastapi import HTTPException
from supabase_auth.errors import AuthApiError

from app.supabase_client import supabase


async def register_user(email: str, password: str, full_name: str) -> dict:
    try:
        response = supabase.auth.sign_up({
            "email": email,
            "password": password,
            "options": {"data": {"full_name": full_name}},
        })
    except AuthApiError as e:
        raise HTTPException(status_code=400, detail=str(e))

    user = response.user
    if user is None:
        raise HTTPException(status_code=400, detail="Registration failed")

    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.user_metadata.get("full_name", ""),
    }


async def login_user(email: str, password: str) -> dict:
    try:
        response = supabase.auth.sign_in_with_password({
            "email": email,
            "password": password,
        })
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail=str(e))

    return {
        "access_token": response.session.access_token,
        "token_type": "bearer",
    }


async def get_user_from_token(token: str) -> dict:
    try:
        response = supabase.auth.get_user(token)
    except AuthApiError as e:
        raise HTTPException(status_code=401, detail=str(e))

    user = response.user
    return {
        "id": user.id,
        "email": user.email,
        "full_name": user.user_metadata.get("full_name", ""),
    }
