import os
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import routes

app = FastAPI()



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


@app.on_event('startup')
def on_startup():
    create_db_and_tables()

app.include_router(routes.router)

class Hola(SQLModel):
    hola: str
    conatras: str
    gs: int

@app.post('/', response_model=Hola)
async def holaa(hola: Hola):
    print(f'Su objeto es {hola}')
    return hola
