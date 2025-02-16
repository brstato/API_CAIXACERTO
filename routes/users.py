from fastapi import APIRouter, Depends, HTTPException
from database import get_db
from schemes import UserCreate, UserRequest, UserResponse
from datetime import datetime
from typing import List

router = APIRouter(prefix="/users")



@router.post("/create_user/", response_model=str)
async def create_user(user: UserCreate, cursor=Depends(get_db)):
    try:
        await cursor.execute(
            "INSERT INTO USERS (NOME, SENHA, EMAIL, CRIADO_EM, STATUS) VALUES (%s, %s, %s, %s, %s)",
            (user.username, user.password, user.email, str(datetime.utcnow()), 'TESTE')
        )
        return "Usuario criado com sucesso!"
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao salvar registro: {str(e)}"
        )
    

    
@router.post("/get_user", response_model=UserResponse)
async def get_user(request: UserRequest, cursor = Depends(get_db)):
    try:
        await cursor.execute(
            "SELECT ID_INT, NOME, EMAIL, SENHA, CRIADO_EM, STATUS FROM USERS WHERE EMAIL = %s",
            (request.email,)
        )
        user = await cursor.fetchone()
        if user:
            if request.password != user['SENHA']:
                raise HTTPException(status_code=401, detail="Senha incorreta!")

            return UserResponse(
                id=user['ID_INT'],
                name=user['NOME'],
                email=user['EMAIL'],
                date_criation=user['CRIADO_EM'].strftime("%Y-%m-%d %H:%M:%S"),
                status=user['STATUS']
            )
        else:
            raise HTTPException(status_code=404, detail="User not found")
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao acessar o banco de dados: {str(e)}"
        )    