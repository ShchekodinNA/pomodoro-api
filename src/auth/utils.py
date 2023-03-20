from abc import ABC, abstractmethod
from sqlalchemy.orm import Session
from . import models
from .schemas import UserSchemas


class UserCrud(ABC):

    @abstractmethod
    def get_user_by_username(self, username: str) -> UserSchemas.UserBase:
        pass

    @abstractmethod
    def get_user_by_username_to_auth(self, username: str) -> UserSchemas.AuthenticateUser:
        pass

    @abstractmethod
    def save_user(self, user_to_save: UserSchemas.AuthenticateUser) -> None:
        pass


class UserDBCRUD(UserCrud):

    def __init__(self, current_session: Session):
        self.current_session = current_session

    def get_user_by_username(self, username: str) -> UserSchemas.UserBase:
        current_user = self.current_session.query(models.User).filter(
            models.User.username == username).first()
        user_to_return = UserSchemas.UserBase(**current_user.__dict__)
        return user_to_return

    def get_user_by_username_to_auth(self, username: str) -> UserSchemas.AuthenticateUser:
        current_user = self.current_session.query(models.User).filter(
            models.User.username == username).first()
        user_to_return = UserSchemas.AuthenticateUser(**current_user.__dict__)
        return user_to_return

    def save_user(self, user_to_save: UserSchemas.AuthenticateUser) -> None:
        current_user = self.current_session.query(models.User).filter(
            models.User.username == user_to_save.username).first()
        current_user.hashed_password = user_to_save.hashed_password
        current_user.email = user_to_save.email
        current_user.username = user_to_save.username
        current_user.is_active = True
        self.current_session.commit()
