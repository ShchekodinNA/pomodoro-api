from .constants import TOKEN_TYPE
from .utils import UserCrud, secret_manager
from .schemas import UserSchemas
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
                             current_user: UserSchemas.Update) -> bool:
        current_hashed_password = self.crud.get_user_hashed_password_from_username(
            current_user.username)
        if not secret_manager.is_secret_correct(current_hashed_password, update_user.old_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        current_user.password = update_user.new_password
        self.crud.save_user(current_user)
        return True

    def get_auth_token_or_none(self, username: str, password: str) -> AuthenticationToken | None:
        hashed_password_of_user = self.crud.get_user_hashed_password_from_username(
            username)
        if not hashed_password_of_user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        if not secret_manager.is_secret_correct(hashed_password_of_user, password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

        auth_token = secret_manager.generate_jwt_token({'sub': username})
        return_token = AuthenticationToken(
            access_token=auth_token, token_type=TOKEN_TYPE)
        return return_token
