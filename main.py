import os
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import admin_router, booking_router, movie_router, session_router, user_router, rating_router

app = FastAPI()



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

create_db_and_tables()


# @app.on_event('startup')
# def on_startup():
#     create_db_and_tables()
    

@app.on_event('startup')
def on_startup():
    pass


app.include_router(admin_router)
app.include_router(booking_router)
app.include_router(movie_router)
app.include_router(session_router)
app.include_router(user_router)
app.include_router(rating_router)

