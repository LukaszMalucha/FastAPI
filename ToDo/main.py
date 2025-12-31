from fastapi import FastAPI, Depends
from typing import Annotated
from ToDo import models
from ToDo.database import engine, SessionLocal
from sqlalchemy.orm import Session
from ToDo.models import Todos

app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/")
async def read_all(db: db_dependency):
    return db.query(Todos).all()
