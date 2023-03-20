from datetime import datetime, timedelta
from .constants import TOKEN_TYPE, security_env
from .utils import UserCrud
from .schemas import UserSchemas
from pydantic import BaseModel
from passlib.context import CryptContext
from passlib.hash import bcrypt
from jose import JWTError, jwt


pwd_context = CryptContext(
    schemes=[security_env.HASHING_SCHEME],
    deprecated="auto"
)


class AuthenticationToken(BaseModel):
    access_token: str
    token_type: str


class Authenticator:

    def __init__(self, crud: UserCrud) -> None:
        self.crud = crud
    
    def change_user_password(self,
                             update_user: UserSchemas.UpdateUserPassword,
                             current_user: UserSchemas.UserBase) -> bool:
        changing_user = self.crud.get_user_by_username_to_auth(current_user.username)
        hashed_password_of_user = changing_user.hashed_password
        if not self.is_password_correct(hashed_password_of_user, update_user.password):
            return False
        new_hashed_password = self.hash_secret(update_user.new_password)
        changing_user.hashed_password = new_hashed_password
        self.crud.save_user(changing_user)
        return True
            

    def get_auth_token_or_none(self, username: str, password: str) -> AuthenticationToken | None:
        current_user = self.crud.get_user_by_username_to_auth(username)
        if not current_user:
            return None

        
        if not self.is_password_correct(current_user.hashed_password, password):
            return None

        auth_token = self._generate_jwt_token({'sub': username})
        return_token = AuthenticationToken(
            access_token=auth_token, token_type=TOKEN_TYPE)
        return return_token

    @classmethod
    def is_password_correct(cls,
                             hashed_secret: str,
                             password: str) -> bool:
        peppered_password = cls.pepper_secret_by_bcrypt(password)
        return pwd_context.verify(peppered_password, hashed_secret)

    @classmethod
    def _generate_jwt_token(cls, body: dict,
                            expires_delta: timedelta = timedelta(minutes=15)) -> str:
        body_to_encode = body.copy()
        expire = datetime.utcnow() + expires_delta
        body_to_encode.update({'exp': expire})
        jwt_token = jwt.encode(body_to_encode,
                               security_env.SECRET_JWT_KEY,
                               algorithm=security_env.ENCRYPTING_ALGORITHM)
        return jwt_token

    @classmethod
    def pepper_secret_by_bcrypt(cls, secret: str) -> str:
        return bcrypt.using(salt=security_env.PEPER_SECRET).hash(secret)
    
    @classmethod
    def hash_secret(cls, secret: str) -> str:
        peppered_secret = cls.pepper_secret_by_bcrypt(secret)
        hashed_secret = pwd_context.hash(peppered_secret)
        return hashed_secret
