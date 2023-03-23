from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .service import Authenticator
from .exceptions import HTTPException401
from ..database import SessionLocal
from .schemas import UserSchemas
from .utils import UserDBCRUD
from .dependencies import get_current_user_if_active
auth_router = APIRouter(prefix='/authorization', tags=['AUTHORIZATION'])


@auth_router.post('')
async def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        authenticator = Authenticator(crud)
        try:
            token = authenticator.get_auth_token_or_none(
                form_data.username, form_data.password)
        except HTTPException:
            raise HTTPException401
    if not token:
        raise HTTPException401
    return token


@auth_router.post('/update_password')
async def update_password(update_user: UserSchemas.FormPasswordChange,
                   user: UserSchemas.Get = Depends(get_current_user_if_active)):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        authenticator = Authenticator(crud)
        if not authenticator.change_user_password(update_user, user):
            return HTTPException401
    return user
        