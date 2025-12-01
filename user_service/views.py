# user_service/views.py

from flask import request
from user_service.serializers import validate_user_payload, validate_email, validate_address
from user_service import repos
from user_service.events import publish_user_updated

def get_user(user_id: str):
    user = repos.get_user(user_id)
    if not user:
        return {"error": "User not found"}, 404
    return user, 200

def create_user():
    payload = request.get_json()
    err = validate_user_payload(payload)
    if err:
        return {"error": err}, 400

    user = repos.create_user(payload["email"], payload["address"])
    return user, 201

def update_user_email(user_id: str):
    payload = request.get_json()
    err = validate_email(payload)
    if err:
        return {"error": err}, 400

    updated = repos.update_user(user_id, email=payload["email"])
    if not updated:
        return {"error": "User not found"}, 404

    publish_user_updated(user_id, "email", payload["email"])
    return {"message": "Email updated"}, 200

def update_user_address(user_id: str):
    payload = request.get_json()
    err = validate_address(payload)
    if err:
        return {"error": err}, 400

    updated = repos.update_user(user_id, address=payload["address"])
    if not updated:
        return {"error": "User not found"}, 404

    publish_user_updated(user_id, "address", payload["address"])
    return {"message": "Address updated"}, 200
