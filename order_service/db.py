# order_service/db.py

import os
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

MONGO_URI = os.getenv("MONGO_URI")
MONGO_DB = os.getenv("MONGO_DB", "orderDB")
MONGO_COLLECTION = os.getenv("MONGO_COLLECTION", "orders")

if not MONGO_URI:
    raise Exception("MONGO_URI not found in .env")

client = MongoClient(MONGO_URI, server_api=ServerApi('1'))

try:
    client.admin.command("ping")
    print("✅ OrderService MongoDB connected successfully.")
except Exception as e:
    print("❌ MongoDB error:", e)

db = client[MONGO_DB]
orders_collection = db[MONGO_COLLECTION]
