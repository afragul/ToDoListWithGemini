import os
from datetime import timedelta , datetime ,timezone
from typing import Annotated
from sqlalchemy.orm import Session
from fastapi import APIRouter , Depends ,HTTPException
from pydantic import BaseModel
from starlette import status
from fastapi.security import OAuth2PasswordRequestForm , OAuth2PasswordBearer
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from jose import jwt, JWTError

router= APIRouter(
    prefix= "/auth",
    tags=["Authentication"],
)

#SECRET_KEY = os.getenv("SECRET_KEY") eger daha iyi calismak istersen
SECRET_KEY = "hyj5dza4my6b17ajfr652zhv3a9jzfcw"  #jwt icin anahtar kelime
ALGORITHM = "HS256" #jwt icin

def get_db():
    db=SessionLocal()
    try:
        yield db #return gibi bi sey
    finally:
        db.close() #session kapandi

db_dependency= Annotated[Session, Depends(get_db)] #session acilir

bcrypt_context=CryptContext(schemes=["bcrypt"], deprecated="auto") #obje olusturuldu. bcrypt algoritmasi kullanilacak

oauth2_bearer=OAuth2PasswordBearer(tokenUrl="/auth/login")

class RegisterUserRequest(BaseModel): #register endpointi icin gerekli
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    roles: str

class Token(BaseModel):
    access_token: str
    token_type: str



def create_access_token(username: str , user_id: int, roles:str , expires_delta: timedelta ): #exprise kismi tokenin ne kadar gecerli olacagini belirler
    payload={'sub':username,
            'id': user_id ,
            'roles' : roles} #json web tokeninda lazim olacagini dusundugumuz seyler bunlar
    expires = datetime.now(timezone.utc) + expires_delta #suan calistigi andan exp delta kadar gecerli olacak
    payload.update({'exp':expires})
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)


def authenticate_user(username: str, password: str , db): #ne ile dogrulama yapilacaksa onlar alinir
    user=db.query(Users).filter(Users.username==username).first() #eslesen kullanici bakildi
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False #password ile userin hash passwordu eslesmedi
    return user #kullanici bulundu authenticate edildi


async def current_user(token: Annotated[str , Depends(oauth2_bearer)]):
    try:
        payload= jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub')
        user_id: int = payload.get('id')
        roles: str = payload.get('roles')

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
        return {'username': username, 'id': user_id, 'roles': roles}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid Token")




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

@router.post("/login" , response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()] ,
                                 db: db_dependency ): #bu form direkt alindi biz olusturmadik
    user= authenticate_user(form_data.username , form_data.password , db)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")

    token= create_access_token(user.username, user.id, user.roles, timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}






















