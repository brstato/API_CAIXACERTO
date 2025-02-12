from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.middleware.gzip import GZipMiddleware
from pydantic_settings import BaseSettings
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List
import asyncmy 
from asyncmy.cursors import DictCursor
import uvicorn
import os

load_dotenv()

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=100, compresslevel=5)
router_test = APIRouter(prefix="/test")

class Settings(BaseModel):
    db_host: str = os.getenv("DB_HOST")
    db_port: int = int(os.getenv("DB_PORT"))
    db_user: str = os.getenv("DB_USER")
    db_pass: str = os.getenv("DB_PASSWORD")
    db_name: str = os.getenv("DB_NAME")

    secrt_key: str = os.getenv("SECRET_KEY")




class Users(BaseModel):
    id: int
    name: str
    password: str
    email: str
    date_criation: str

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


# Dependência para obter sessão do banco
async def get_db(): 
    pool = app.state.pool
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            yield cursor

@router_test.get("/", response_model=List[Users])
async def List_Users(cursor = Depends(get_db)):
    try:
        await cursor.execute("SELECT * FROM USERS")
        rows = await cursor.fetchall()
        
        # Converter resultados para o modelo Pydantic
        #users = []
        return [
            Users(
                id=row['ID_INT'],
                name=row['NOME'],
                password=row['SENHA'],
                email=row['EMAIL'],
                date_criation=row['CRIADO_EM'].strftime("%Y-%m-%d %H:%M:%S")
            ) for row in rows
        ]
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {str(e)}"

        )
    
app.include_router(router_test)

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