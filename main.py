from fastapi import FastAPI , Depends
from fastapi.params import Depends
from typing import Annotated
from sqlalchemy.orm import Session
from models import Base,ToDo
from database import engine, SessionLocal

app=FastAPI()

Base.metadata.create_all(bind=engine) #bu satir db olusturur

def get_db():
    db=SessionLocal()
    try:
        yield db #return gibi bi sey
    finally:
        db.close() #session kapandi

#tum endpointler bu fonka depend edecek artik

db_dependency= Annotated[Session, Depends(get_db)]

@app.get("/read_all")
async def read_all(db:db_dependency):
    return db.query(ToDo).all()

