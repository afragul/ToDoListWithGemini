from fastapi import FastAPI , Request
from fastapi.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

from .models import Base
from .database import engine
from .routers.auth import router as auth_router
from .routers.todo import router as todo_router
import os
app=FastAPI()

script_dir=os.path.dirname(__file__)

app.mount("/static" , StaticFiles(directory="static"), name="static")

@app.get("/")
def read_root(request: Request): #baslangic sayfasi. bu req ile cookie ye vs her seye ulasabilirsiniz
    return RedirectResponse(url="/todo/todo-page" , status_code=302)
app.include_router(auth_router) #routerlar eklemek
app.include_router(todo_router) #routerlar eklemek

Base.metadata.create_all(bind=engine) #bu satir db olusturur ana uygulama ile alakali
