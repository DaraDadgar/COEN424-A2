from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields
from user_service.views import (
    create_user,
    update_user_email,
    update_user_address,
    get_user
)

api = Blueprint("api", __name__)

restx = Api(
    api,
    version="1.0",
    title="User Microservice API",
    description="Manage users, email changes, address changes with event sync",
    doc="/docs"
)

user_ns = restx.namespace("users", description="User operations")

# ---------- Swagger Models ----------
user_model = restx.model("User", {
    "userId": fields.String(example="u123"),
    "email": fields.String(example="test@example.com"),
    "address": fields.String(example="123 Street, Montreal"),
})

create_user_payload = restx.model("CreateUserPayload", {
    "email": fields.String(required=True),
    "address": fields.String(required=True)
})

update_email_payload = restx.model("UpdateEmailPayload", {
    "email": fields.String(required=True)
})

update_address_payload = restx.model("UpdateAddressPayload", {
    "address": fields.String(required=True)
})

# ----------- Routes -------------

@user_ns.route("/")
class UserCreate(Resource):
    @user_ns.expect(create_user_payload)
    @user_ns.marshal_with(user_model, code=201)
    def post(self):
        """Create a new user"""
        return create_user()


@user_ns.route("/<string:user_id>/email")
class UserEmail(Resource):
    @user_ns.expect(update_email_payload)
    def put(self, user_id):
        """Update user email (triggers event)"""
        return update_user_email(user_id)

@user_ns.route("/<string:user_id>/address")
class UserAddress(Resource):
    @user_ns.expect(update_address_payload)
    def put(self, user_id):
        """Update user address (triggers event)"""
        return update_user_address(user_id)
@user_ns.route("/<string:user_id>")
class UserGet(Resource):
    @user_ns.marshal_with(user_model, code=200)
    def get(self, user_id):
        """Get user info"""
        return get_user(user_id)