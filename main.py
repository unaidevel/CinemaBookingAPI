import os
from fastapi import FastAPI
from sqlmodel import SQLModel
from app.database import engine
from app.routers import admin_router, booking_router, movie_router, session_router, user_router, rating_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()



def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# create_db_and_tables()


origins = [
    "http://localhost:3000",     # React (desarrollo)
    "http://127.0.0.1:3000",
    "http://localhost:5173",     # Vite
    "http://127.0.0.1:5173",
    "http://localhost:5500",     # Live Server (HTML puro)
    "http://127.0.0.1:5500",
]


app.add_middleware(
    CORSMiddleware, 
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=["*"],
)


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

