import asyncmy 
from asyncmy.cursors import DictCursor
from fastapi import Request
import schemes

async def get_db_pool():
    settings = schemes.Settings()
    return await asyncmy.create_pool(
        host=settings.db_host,
        port=settings.db_port,
        user=settings.db_user,
        password=settings.db_pass,
        db=settings.db_name,
        autocommit=True,
        maxsize=20,
    )  

async def get_db(request: Request):
    pool = request.app.state.pool 
    async with pool.acquire() as conn:
        async with conn.cursor(DictCursor) as cursor:
            yield cursor