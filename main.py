from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime, timedelta
import jwt
import bcrypt
import asyncmy 
from asyncmy.cursors import DictCursor
import uvicorn
import os

load_dotenv()

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=100, compresslevel=5)
router_test = APIRouter(prefix="/test")
router_users = APIRouter(prefix="/users")
auth_router=APIRouter(prefix="/auth")
oauth_scheme = OAuth2PasswordBearer(tokenUrl="/auth/token")

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

class Users(BaseModel):
    id: int
    name: str
    password: str
    email: str
    date_criation: str

class UserCreate(BaseModel):
    username: str
    email: str
    password: str

class Token(BaseModel):
    acces_token: str
    token_type: str        

@app.on_event("startup")
async def startup():
    settings = Settings()
    app.state.pool = await asyncmy.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_pass,
        db=settings.db_name,
        autocommit=True,
        maxsize=20,
    )
   

@app.on_event("shutdown")
async def shutdown():
    pool = app.state.pool
    pool.close()
    await pool.wait_closed()


def hash_password(password: str) -> str:
    return bcrypt.hashpw(
        password.encode("utf-8"), 
        bcrypt.gensalt()
    ).decode("utf-8")


async def get_db(): 
    pool = app.state.pool
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            yield cursor





@app.post("/create_user/")
async def create_user(name: str, email: str, password: str, cursor=Depends(get_db)):
    try:
        await cursor.execute(
            "INSERT INTO USERS (NOME, SENHA, EMAIL, CRIADO_EM) VALUES (%s, %s, %s, %s)",
            (name, email, password, str(datetime.utcnow()))
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar registro: {str(e)}"
        )

@router_test.get("/", response_model=List[Users])
async def List_Users(cursor = Depends(get_db)):
    try:
        await cursor.execute("SELECT * FROM USERS")
        rows = await cursor.fetchall()
        
        users = [
            Users(
                id=row['ID_INT'],
                name=row['NOME'],
                password=row['SENHA'],
                email=row['EMAIL'],
                date_criation=row['CRIADO_EM'].strftime("%Y-%m-%d %H:%M:%S")
            ) for row in rows
        ]

        return users

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {str(e)}"

        )
    
app.include_router(router_test)
app.include_router(router_users)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0", 
        port=20000,
        workers=3,
        http="httptools",
        loop="uvloop",
        reload=True
    )