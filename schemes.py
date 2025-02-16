from pydantic import BaseModel, EmailStr
from typing import Optional
import os

class Settings(BaseModel):
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT"))
    db_user: str = os.getenv("DB_USER")
    db_pass: str = os.getenv("DB_PASSWORD")
    db_name: str = os.getenv("DB_NAME")

class Settings_Autentication(BaseModel):
    secrt_key: str = os.getenv("SECRET_KEY")
    algorithm: str = os.getenv("ALGORITHM")
    acces_token_expire_minutes: int = 30

class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    date_criation: str
    status: str

class UserCreate(BaseModel):
    username: str
    password: str
    email: EmailStr

class UserRequest(BaseModel):
    email: str
    password: str    

class Token(BaseModel):
    acces_token: str
    token_type: str 