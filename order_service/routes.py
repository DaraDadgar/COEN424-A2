# order_service/routes.py

from flask import Blueprint
from flask_restx import Api, Namespace, Resource, fields
from order_service.views import (
    create_order_handler,
    get_orders_by_state_handler,
    update_order_status_handler,
    update_order_contact_handler,
)

api = Blueprint("api", __name__)

restx = Api(
    api,
    version="1.0",
    title="Order Microservice API",
    description="Manage orders and synchronize user info",
    doc="/docs"
)

order_ns = restx.namespace("orders", description="Order operations")

# Swagger models
order_create_model = restx.model("CreateOrder", {
    "order_id": fields.String(required=True),
    "user_id": fields.String(required=True),
    "items": fields.List(fields.String, required=True),
    "email": fields.String(required=True),
    "address": fields.String(required=True),
})

order_status_update_model = restx.model("UpdateStatus", {
    "status": fields.String(required=True, example="shipping"),
})

order_contact_update_model = restx.model("UpdateContact", {
    "email": fields.String(example="user@example.com"),
    "address": fields.String(example="123 Street"),
})

# Routes

@order_ns.route("/")
class OrdersByStatus(Resource):
    def get(self):
        """Get orders by status using ?status="""
        return get_orders_by_state_handler()


@order_ns.route("/")
class OrderCreate(Resource):
    @order_ns.expect(order_create_model)
    def post(self):
        """Create a new order"""
        return create_order_handler()


@order_ns.route("/<string:order_id>/status")
class OrderStatus(Resource):
    @order_ns.expect(order_status_update_model)
    def put(self, order_id):
        """Update order status"""
        return update_order_status_handler(order_id)


@order_ns.route("/<string:order_id>/contact")
class OrderContact(Resource):
    @order_ns.expect(order_contact_update_model)
    def put(self, order_id):
        """Update email or address"""
        return update_order_contact_handler(order_id)
