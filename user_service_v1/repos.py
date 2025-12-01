# user_service/repos.py
import uuid
from user_service_v1.db import users_collection

def create_user(email: str, delivery_address: str):
    # Example _id format: "U001", "U002", ...
    last_user = users_collection.find_one(sort=[("_id", -1)])
    if last_user:
        next_id = "U" + str(int(last_user["_id"][1:]) + 1).zfill(3)
    else:
        next_id = "U001"

    doc = {
        "_id": next_id,
        "email": email,
        "delivery_address": delivery_address
    }

    users_collection.insert_one(doc)
    return doc

def get_user(user_id: str):
    return users_collection.find_one({"_id": user_id}, {"_id": 1, "email": 1, "delivery_address": 1})



def update_user(user_id: str, email=None, address=None):
    update_fields = {}

    if email:
        update_fields["email"] = email

    if address:
        update_fields["delivery_address"] = address

    if not update_fields:
        return False

    result = users_collection.update_one(
        {"_id": user_id},
        {"$set": update_fields}
    )

    return result.matched_count > 0
