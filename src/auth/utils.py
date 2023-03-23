from abc import ABC, abstractmethod
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from passlib.hash import bcrypt
from passlib.context import CryptContext
from . import models
from .schemas import UserSchemas
from .models import User
from .constants import security_env
from .exceptions import HTTPException400
from jose import jwt


class _SecretController:
    def __init__(self) -> None:
        self.pwd_context = CryptContext(
            schemes=[security_env.HASHING_SCHEME],
            deprecated="auto"
        )

    def is_secret_correct(self,
                          hashed_secret: str,
                          secret_to_check: str) -> bool:
        peppered_password = self.pepper_secret_by_bcrypt(secret_to_check)
        return self.pwd_context.verify(peppered_password, hashed_secret)

    def generate_jwt_token(self, body: dict,
                           expires_delta: timedelta = timedelta(minutes=15)) -> str:
        body_to_encode = body.copy()
        expire = datetime.utcnow() + expires_delta
        body_to_encode.update({'exp': expire})
        jwt_token = jwt.encode(body_to_encode,
                               security_env.SECRET_JWT_KEY,
                               algorithm=security_env.ENCRYPTING_ALGORITHM)
        return jwt_token

    def pepper_secret_by_bcrypt(self, secret: str) -> str:
        return bcrypt.using(salt=security_env.PEPER_SECRET).hash(secret)

    def hash_secret(self, secret: str) -> str:
        peppered_secret = self.pepper_secret_by_bcrypt(secret)
        hashed_secret = self.pwd_context.hash(peppered_secret)
        return hashed_secret


secret_manager = _SecretController()


class UserCrud(ABC):

    @abstractmethod
    def get_user_by_username(self, username: str) -> UserSchemas.Get:
        pass

    @abstractmethod
    def get_user_hashed_password_from_username(self, username: str) -> UserSchemas.Get:
        pass

    @abstractmethod
    def save_user(self, user_to_save: UserSchemas.Update) -> None:
        pass


class UserDBCRUD(UserCrud):

    def __init__(self, current_session: Session):
        self.current_session = current_session

    def get_user_by_username(self, username: str) -> UserSchemas.Get:
        current_user = self.current_session.query(models.User).filter(
            models.User.username == username).first()
        if current_user is None:
            raise HTTPException400
        user_to_return = UserSchemas.Get(**current_user.__dict__)
        return user_to_return

    def get_user_hashed_password_from_username(self, username: str) -> str:
        current_user = self.current_session.query(models.User).filter(
            models.User.username == username).first()
        if current_user is None:
            raise HTTPException400
        return current_user.hashed_password

    def save_user(self, user_to_save: UserSchemas.Update) -> None:
        current_user: User = self.current_session.query(
            models.User).get(user_to_save.id)
        dict_current_user = user_to_save.dict(exclude={'id', 'hashed_password'}).items()
        for key, value in dict_current_user:
            if value is not None:
                setattr(current_user, key, value)
        if user_to_save.password is not None:
            new_hashed_password = secret_manager.hash_secret(user_to_save.password)
            current_user.hashed_password = new_hashed_password
        self.current_session.flush()
