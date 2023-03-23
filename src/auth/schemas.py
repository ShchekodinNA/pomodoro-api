from pydantic import BaseModel, Field


password_field = Field(max_length=40, min_length=6, default=None)
username_field = Field(
    regex=r"(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", max_length=20, min_length=5)


class UserSchemas:
    class Get(BaseModel):
        id: int
        username: str
        email: str
        is_active: bool

    class Create(BaseModel):
        username: str
        email: str
        is_active: bool
        password: str = password_field

    class Update(BaseModel):
        id: int
        username: str | None = None
        email: str | None = None
        is_active: bool | None = None
        password: str | None = password_field

    class Delete(BaseModel):
        id: str
        
    class FormPasswordChange(BaseModel):
        old_password: str = password_field
        new_password: str = password_field