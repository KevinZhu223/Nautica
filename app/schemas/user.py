from pydantic import BaseModel, EmailStr, conint, constr, validator
from typing import List, Optional

class TokenResponse(BaseModel):
    access_token: str
    token_type: str


class UserBase(BaseModel):
    name: str
    email: EmailStr


class ResetPassword(BaseModel):
    old_password: str
    new_password: str


class ForgotPassword(BaseModel):
    email: EmailStr


class FPAccept(ForgotPassword):
    code: int
    password: str
    confirm_password: str


class UserCreate(UserBase):
    password: str

class UserPatch(BaseModel):
    name: Optional[str]
    email: Optional[EmailStr]

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True

class UserResponseCurrent(BaseModel):
    id: int
    name: str
    email: EmailStr

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    email: str
    password: str
