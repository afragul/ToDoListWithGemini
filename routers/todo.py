from fastapi import APIRouter , Depends ,HTTPException , Path ,Request
from typing import Annotated

from pydantic import BaseModel , Field
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse

from routers.auth import current_user
from models import Base,ToDo
from database import engine, SessionLocal
from fastapi.templating import Jinja2Templates
router=APIRouter(
    prefix= "/todo", #tum endpointlerin basina koyar
    tags=["ToDO"], #docs da ayirmamiza yaradi
)

#burda sadece to-do ile alakali seyler olmali. req, kendi endpointleri vs vs

templates = Jinja2Templates(directory="templates")

class ToDoRequest(BaseModel):
    title: str =Field(min_length=3)
    description: str =Field(min_length=3 , max_length=1000)
    priority: int =Field(gt=0,lt=6)
    completed: bool =False

def get_db():
    db=SessionLocal()
    try:
        yield db #return gibi bi sey
    finally:
        db.close() #session kapandi

#tum endpointler bu fonka depend edecek artik

db_dependency= Annotated[Session, Depends(get_db)] #session acilir
user_dep=Annotated[dict, Depends(current_user)]


def redirect_to_login(): #yardimci fonk
    redirect_response=RedirectResponse(url="/auth/login-page", status_code=302)
    redirect_response.delete_cookie("access_token")
    return redirect_response


#sayfalar
@router.get("/todo-page")
async def render_todo_page(request: Request , db: db_dependency):
    try:
        user= await current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todos= db.query(ToDo).filter(ToDo.owner_id == user.get("id")).all()

        return templates.TemplateResponse("todo.html",{"request":request,"todos":todos , "user":user})
    except:
        return redirect_to_login()



@router.get("/add-todo-page")
async def render_add_todo_page(request: Request ):
    try:
        user= await current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        return templates.TemplateResponse("add-todo.html",{"request":request , "user":user})
    except:
        return redirect_to_login()


@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request ,todo_id:int ,db: db_dependency):
    try:
        user= await current_user(request.cookies.get("access_token"))
        if user is None:
            return redirect_to_login()

        todo=db.query(ToDo).filter(ToDo.id == todo_id).first()

        return templates.TemplateResponse("edit-todo.html",{"request":request ,"todo" :todo ,"user":user})
    except:
        return redirect_to_login()



@router.get("/get_all")
async def get_all(user:user_dep, db:db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    return db.query(ToDo).filter(ToDo.owner_id==user.get('id')).all()

@router.get("/todo/{todoId}" , status_code=status.HTTP_200_OK)
async def get_by_id(user:user_dep, db:db_dependency ,todoId: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    todo =db.query(ToDo).filter(ToDo.id==todoId).filter(ToDo.owner_id==user.get('id')).first()

    if todo is not None:
        return todo
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")



@router.post("/todo",status_code=status.HTTP_201_CREATED)
async def create_todo(user:user_dep, db:db_dependency , todo_request: ToDoRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    todo=ToDo(**todo_request.dict(),owner_id=user.get('id'))
    db.add(todo)
    db.commit()

@router.put("/todo/{id}" , status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user:user_dep, db:db_dependency, todo_request: ToDoRequest, id: int=Path(gt=0) ):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo =db.query(ToDo).filter(ToDo.id==id).filter(ToDo.owner_id==user.get('id')).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")
    todo.title=todo_request.title
    todo.priority=todo_request.priority
    todo.description=todo_request.description
    todo.completed=todo_request.completed

    db.add(todo)
    db.commit()


@router.delete("/todo/{id}" , status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user:user_dep, db:db_dependency, id: int=Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)

    todo =db.query(ToDo).filter(ToDo.id==id).filter(ToDo.owner_id==user.get('id')).first()

    if todo is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Not Found")

    db.query(ToDo).filter(ToDo.id==id).delete()
    db.commit()








