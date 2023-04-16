from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from .service import Authenticator
from .exceptions import HTTPException401
from ..database import SessionLocal
from .schemas import UserSchemas
from .utils import UserDBCRUD
from .dependencies import get_current_user_if_active
auth_router = APIRouter(prefix='/authorization', tags=['AUTHORIZATION'])


@auth_router.post('')
def authenticate(form_data: OAuth2PasswordRequestForm = Depends()):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        authenticator = Authenticator(crud)
        try:
            token = authenticator.get_auth_token_or_none(
                form_data.username, form_data.password)
        except HTTPException as exc:
            raise HTTPException401 from exc
    if not token:
        raise HTTPException401
    return token


@auth_router.post('/update_password')
def update_password(password_form: UserSchemas.FormPasswordChange,
                   user: UserSchemas.Get = Depends(get_current_user_if_active)):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        authenticator = Authenticator(crud)
        authenticator.change_user_password(password_form, user)
        session.commit()
    return user

@auth_router.post('/user')
def create_user(new_user: UserSchemas.Create):
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        crud.create_user(new_user)
        session.commit()
    return new_user
