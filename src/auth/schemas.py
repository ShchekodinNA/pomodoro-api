from pydantic import BaseModel, Field


password_field = Field(max_length=40, min_length=6)

class UserSchemas:
    class _ActiveUser(BaseModel):
        is_active: bool = True
    
    class _UserPassword(BaseModel):
        password: str = password_field
    
    class UserBase(_ActiveUser):
        """Read, Delete"""
        username: str = Field(regex=r"(?![_.])(?!.*[_.]{2})[a-zA-Z0-9._]+(?<![_.])$", max_length=20, min_length=5)
        email: str
        
        
    class CreateUser(UserBase):
        """Create"""
        
    
    class AuthenticateUser(UserBase):
        hashed_password: str

    class UpdateUserPassword(_UserPassword):
        """Update"""
        new_password: str = password_field
    
        