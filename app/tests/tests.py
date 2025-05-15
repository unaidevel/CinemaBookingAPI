# tests/test_movies.py
import pytest
from httpx import AsyncClient
from sqlmodel import SQLModel, Session
from main import app
from app.models import Movie, GenreEnum
from app.database import engine

from datetime import date

@pytest.fixture(name="client")
async def client_fixture():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac


@pytest.fixture(name="test_movie_data")
def movie_data():
    return {
        "title": "Test Movie",
        "description": "A movie for testing",
        "release_date": str(date.today()),
        "duration": 120,
        "genre": "action"
    }


@pytest.fixture(name="admin_token")
def fake_admin_token():
    # En tu sistema real, deberías generar un token real aquí
    return "Bearer faketokenforadminuser"


@pytest.fixture(autouse=True)
def prepare_db():
    # Borra y crea de nuevo las tablas para cada test
    SQLModel.metadata.drop_all(engine)
    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)



@pytest.mark.asyncio    #Movie creation
async def test_create_movie(client, test_movie_data, admin_token):
    response = await client.post("/movie", json=test_movie_data, headers={"Authorization": admin_token})
    assert response.status_code == 200
    data = response.json()
    assert data["title"] == test_movie_data["title"]
    assert "slug" in data



@pytest.mark.asyncio    #Read movie by slug
async def test_read_movie_by_slug(client, test_movie_data, admin_token):
    # Crear primero
    res = await client.post("/movie", json=test_movie_data, headers={"Authorization": admin_token})
    slug = res.json()["slug"]

    # Leer
    response = await client.get(f"/movie/{slug}")
    assert response.status_code == 200
    assert response.json()["title"] == test_movie_data["title"]



@pytest.mark.asyncio   #Read movies
async def test_read_movies(client, test_movie_data, admin_token):
    await client.post("/movie", json=test_movie_data, headers={"Authorization": admin_token})

    response = await client.get("/movie")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["title"] == test_movie_data["title"]


@pytest.mark.asyncio   #Edit movies
async def test_update_movie(client, test_movie_data, admin_token):
    res = await client.post("/movie", json=test_movie_data, headers={"Authorization": admin_token})
    slug = res.json()["slug"]

    update_data = {"duration": 150}
    response = await client.patch(f"/movie/{slug}", json=update_data, headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json()["duration"] == 150



@pytest.mark.asyncio #delete movies
async def test_delete_movie(client, test_movie_data, admin_token):
    res = await client.post("/movie", json=test_movie_data, headers={"Authorization": admin_token})
    slug = res.json()["slug"]

    response = await client.delete(f"/movie/{slug}", headers={"Authorization": admin_token})
    assert response.status_code == 200
    assert response.json()["message"] == "Movie deleted successfully!"

    # Verifica que ya no está
    response = await client.get(f"/movie/{slug}")
    assert response.status_code == 404