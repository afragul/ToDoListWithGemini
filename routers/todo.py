from fastapi import APIRouter , Depends ,HTTPException , Path
from typing import Annotated

from pydantic import BaseModel , Field
from sqlalchemy.orm import Session
from starlette import status

from models import Base,ToDo
from database import engine, SessionLocal

router=APIRouter(
    prefix= "/todo", #tum endpointlerin basina koyar
    tags=["ToDO"], #docs da ayirmamiza yaradi
)

#burda sadece to-do ile alakali seyler olmali. req, kendi endpointleri vs vs

class ToDoRequest(BaseModel):
    title: str =Field(min_length=3)
    description: str =Field(min_length=3 , max_length=1000)
    priority: int =Field(gt=0,lt=6)
    completed: bool

def get_db():
    db=SessionLocal()
    try:
        yield db #return gibi bi sey
    finally:
        db.close() #session kapandi

#tum endpointler bu fonka depend edecek artik

db_dependency= Annotated[Session, Depends(get_db)] #session acilir

@router.get("/get_all")
async def get_all(db:db_dependency):
    return db.query(ToDo).all()

@router.get("/get_by_id/{id}" , status_code=status.HTTP_200_OK)
async def get_by_id( db:db_dependency ,id: int=Path(gt=0)):
    todo =db.query(ToDo).filter(ToDo.id==id).first()  #filtrelemis olduk ama liste dondu
    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")



@router.post("/create",status_code=status.HTTP_201_CREATED)
async def create_todo(db:db_dependency , todo_request: ToDoRequest):
    todo=ToDo(**todo_request.dict())
    db.add(todo)
    db.commit()

@router.put("/update/{id}" , status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(db:db_dependency, todo_request: ToDoRequest, id: int=Path(gt=0) ):
    todo=db.query(ToDo).filter(ToDo.id==id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")
    todo.title=todo_request.title
    todo.priority=todo_request.priority
    todo.description=todo_request.description
    todo.completed=todo_request.completed

    db.add(todo)
    db.commit()


@router.delete("/delete/{id}" , status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(db:db_dependency, id: int=Path(gt=0)):
    todo=db.query(ToDo).filter(ToDo.id==id).first()
    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")

    db.query(ToDo).filter(ToDo.id==id).delete()
    db.commit()








