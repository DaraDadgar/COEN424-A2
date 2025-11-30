# order_service/views.py

from flask import request
from order_service import repos

def create_order_handler():
    data = request.get_json()
    order = repos.create_order(
        data["order_id"],
        data["user_id"],
        data["items"],
        data["email"],
        data["address"]
    )
    return {"message": "Order created", "order": order}, 201


def get_orders_by_state_handler():
    status = request.args.get("status")
    if not status:
        return {"error": "Missing ?status"}, 400
    orders = repos.get_orders_by_status(status)
    return {"orders": orders}, 200


def update_order_status_handler(order_id):
    data = request.get_json()
    if "status" not in data:
        return {"error": "Missing status"}, 400
    ok = repos.update_order_status(order_id, data["status"])
    return {"updated": ok}, 200


def update_order_contact_handler(order_id):
    data = request.get_json()
    ok = repos.update_contact(order_id, email=data.get("email"), address=data.get("address"))
    return {"updated": ok}, 200
