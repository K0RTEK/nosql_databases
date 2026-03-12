import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
APP_DB = os.getenv("APP_DB", "university_db")


def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_db():
    return get_client()[APP_DB]
