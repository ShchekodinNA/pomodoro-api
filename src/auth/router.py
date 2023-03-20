from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from .service import Authenticator
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
        token = authenticator.get_auth_token_or_none(
            form_data.username, form_data.password)
    if not token:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED)
    return token


@auth_router.post('/update_password')
async def update_password(update_user: UserSchemas.UpdateUserPassword,
                   user: UserSchemas.UserBase = Depends(get_current_user_if_active)):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        authenticator = Authenticator(crud)
        if not authenticator.change_user_password(update_user, user):
            return HTTPException(status.HTTP_401_UNAUTHORIZED)
    return 'Success'
        


@auth_router.post('/test')
async def login(user: UserSchemas.UserBase = Depends(get_current_user_if_active)):
    pass
    return user
