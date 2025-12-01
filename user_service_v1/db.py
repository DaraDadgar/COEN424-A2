# user_service/db.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGO_DB", "users_db")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "users")

client = MongoClient(MONGO_URL)
db = client[MONGO_DB]
users_collection = db[MONGO_COLLECTION]

print("[MongoDB] Connected to:", MONGO_URL)
