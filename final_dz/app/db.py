import os
from dotenv import load_dotenv
from pymongo import MongoClient

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "university_db")


def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)


def get_db():
    return get_client()[MONGO_DB]