from pydantic import BaseSettings
from fastapi.security import OAuth2PasswordBearer
class SecurityEnv(BaseSettings):
    class Config:
        env_file = '.env'
    SECRET_JWT_KEY: str
    TOKEN_LIFETIME_IN_MINTUTES: int
    ENCRYPTING_ALGORITHM: str
    HASHING_SCHEME: str
    PEPER_SECRET: str

TOKEN_TYPE = 'Bearer'

security_env = SecurityEnv()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl='authorization')