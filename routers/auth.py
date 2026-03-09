from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter , Depends ,HTTPException
from pydantic import BaseModel
from starlette import status

from database import SessionLocal
from models import Users
from passlib.context import CryptContext
router= APIRouter(
    prefix= "/auth",
    tags=["Authentication"],
)

def get_db():
    db=SessionLocal()
    try:
        yield db #return gibi bi sey
    finally:
        db.close() #session kapandi

db_dependency= Annotated[Session, Depends(get_db)] #session acilir

bcrypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto") #obje olusturuldu. bcrypt algoritmasi kullanilacak


class RegisterUserRequest(BaseModel): #register endpointi icin gerekli
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    roles: str



@router.post("/register" , status_code=status.HTTP_201_CREATED)
async def register_user(db:db_dependency ,request: RegisterUserRequest):
    user= Users(
        username=request.username,
        email=request.email,
        first_name=request.first_name,
        last_name=request.last_name,
        roles=request.roles,
        is_active= True,
        hashed_password=bcrypt_context.hash(request.password)
    )
    db.add(user)
    db.commit()










