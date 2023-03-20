from typing import Annotated
from .constants import security_env, oauth2_scheme
from ..database import SessionLocal
from .utils import UserDBCRUD
from .schemas import UserSchemas
from fastapi import Depends, status, HTTPException
from jose import jwt, JWTError

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]) -> UserSchemas.UserBase:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token,
                             security_env.SECRET_JWT_KEY,
                             algorithms=[security_env.ENCRYPTING_ALGORITHM])
        username: str = payload.get('sub')
        if username is None:
            raise credentials_exception
    except JWTError as exc:
        raise credentials_exception from exc
    with SessionLocal() as session:
        crud = UserDBCRUD(session)
        current_user = crud.get_user_by_username(username)
    return current_user


async def get_current_user_if_active(user: UserSchemas.UserBase = Depends(get_current_user)) -> UserSchemas.UserBase:
    if user.is_active:
        return user
    raise HTTPException(status.HTTP_401_UNAUTHORIZED)