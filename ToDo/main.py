from fastapi import FastAPI

from ToDo import models
from ToDo.database import engine
from routers import auth, todos, admin

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(admin.router)
app.include_router(auth.router)
app.include_router(todos.router)

