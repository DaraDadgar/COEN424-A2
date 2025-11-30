# order_service/repos.py

from order_service.db import orders_collection

def create_order(order_id, user_id, items, email, address):
    doc = {
        "_id": order_id,
        "user_id": user_id,
        "items": items,
        "user_email": email,
        "delivery_address": address,
        "status": "under process"
    }
    orders_collection.insert_one(doc)
    return doc


def get_orders_by_status(status):
    cursor = orders_collection.find({"status": status}, {"_id": 0})
    return list(cursor)


def update_order_status(order_id, new_status):
    result = orders_collection.update_one(
        {"_id": order_id},
        {"$set": {"status": new_status}}
    )
    return result.matched_count > 0


def update_contact(order_id, email=None, address=None):
    update_fields = {}

    if email:
        update_fields["user_email"] = email
    if address:
        update_fields["delivery_address"] = address

    if not update_fields:
        return False

    result = orders_collection.update_one(
        {"_id": order_id},
        {"$set": update_fields}
    )
    return result.matched_count > 0


# For RabbitMQ sync (update multiple orders for a user)
def update_orders_by_user(user_id, field, new_value):
    field_map = {
        "email": "user_email",
        "address": "delivery_address",
    }

    if field not in field_map:
        return False

    mongo_field = field_map[field]

    result = orders_collection.update_many(
        {"user_id": user_id},
        {"$set": {mongo_field: new_value}}
    )

    return result.modified_count
