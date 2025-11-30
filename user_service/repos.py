# user_service/repos.py
import uuid
from user_service.db import users_collection

def create_user(email: str, address: str):
    user_id = f"u::{uuid.uuid4()}"
    doc = {
        "user_id": user_id,
        "email": email,
        "address": address
    }
    users_collection.insert_one(doc)
    return doc

def get_user(user_id: str):
    doc = users_collection.find_one({"user_id": user_id}, {"_id": 0})
    return doc


def update_user(user_id: str, email=None, address=None):
    update_fields = {}
    if email:
        update_fields["email"] = email
    if address:
        update_fields["delivery_address"] = address

    if not update_fields:
        return False

    result = users_collection.update_one(
        {"userId": user_id},
        {"$set": update_fields}
    )

    # matched_count=0 → user not found
    return result.matched_count > 0
