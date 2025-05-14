
from dotenv import load_dotenv
import os


load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
SECRET_KEY = os.getenv("SECRET_KEY")



# from pydantic_settings import BaseSettings, SettingsConfigDict
# from functools import lru_cache

# class Settings(BaseSettings):
#     SECRET_KEY: str
#     DATABASE_URL: str


#     model_config = SettingsConfigDict(env_file="/home/unai/Desktop/Portfolio/portfolio_project/backend/CourtBookingAPI/.env")


# @lru_cache
# def get_settings() -> Settings:
#     return Settings()


