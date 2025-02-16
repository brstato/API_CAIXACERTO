from fastapi import FastAPI, APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from typing import List, Optional
from datetime import datetime, timedelta
from database import get_db_pool, get_db
from routes.users import router as users_routes
from schemes import Settings, Settings_Autentication, UserCreate, UserRequest,  Token
import asyncmy 
import schemes
from asyncmy.cursors import DictCursor
import jwt
import uvicorn
import database

load_dotenv()

app = FastAPI()
app.add_middleware(GZipMiddleware, minimum_size=100, compresslevel=5)

@app.on_event("startup")
async def startup():
    app.state.pool = await get_db_pool()

@app.on_event("shutdown")
async def shutdown():
    pool = app.state.pool
    pool.close()
    await pool.wait_closed()

async def get_db_dependency():
    return get_db(app.state.pool)

app.include_router(users_routes)

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