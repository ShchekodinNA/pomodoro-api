from .constants import TOKEN_TYPE
from .utils import UserCrud, secret_manager
from .schemas import UserSchemas
from .exceptions import HTTPException400, HTTPException401
from pydantic import BaseModel
from fastapi import HTTPException, status

class AuthenticationToken(BaseModel):
    access_token: str
    token_type: str


class Authenticator:

    def __init__(self, crud: UserCrud) -> None:
        self.crud = crud

    def change_user_password(self,
                             update_user: UserSchemas.FormPasswordChange,
                             current_user: UserSchemas.Get) -> None:
        if update_user.new_password == update_user.old_password:
            raise HTTPException400
        current_hashed_password = self.crud.get_user_hashed_password_from_username(
            current_user.username)
        if not secret_manager.is_secret_correct(current_hashed_password, update_user.old_password):
            raise HTTPException401
        current_user_dict = current_user.dict()
        current_user_dict['password'] = update_user.new_password
        user_to_save = UserSchemas.Update(**current_user_dict)
        self.crud.save_user(user_to_save)
        
    def get_auth_token_or_none(self, username: str, password: str) -> AuthenticationToken:
        hashed_password_of_user = self.crud.get_user_hashed_password_from_username(
            username)
        if not hashed_password_of_user:
            raise HTTPException401

        if not secret_manager.is_secret_correct(hashed_password_of_user, password):
            raise HTTPException401

        auth_token = secret_manager.generate_jwt_token({'sub': username})
        return_token = AuthenticationToken(
            access_token=auth_token, token_type=TOKEN_TYPE)
        return return_token
