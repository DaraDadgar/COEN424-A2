from flask import Flask, request, Response
import requests
import json
import random

app = Flask(__name__)

def load_config():
    """Load routing config dynamically each request."""
    with open("gateway_config.json") as f:
        return json.load(f)

def forward_request(target_url):
    """Generic forwarding helper to send request to target microservice."""
    response = requests.request(
        method=request.method,
        url=target_url,
        headers={key: value for key, value in request.headers if key.lower() != "host"},
        params=request.args,
        json=request.get_json(silent=True),
    )
    return Response(response.content, status=response.status_code, headers=response.headers.items())


@app.route("/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/users", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
def route_user_request(path):
    config = load_config()
    P = config.get("routing_percentage_v1", 0.5)

    # Decide routing based on probability P
    if random.random() < P:
        target = f"{config['v1_url']}/users/{path}"
        version = "v1"
    else:
        target = f"{config['v2_url']}/users/{path}"
        version = "v2"

    print(f"[GATEWAY] → {version.upper()} handling request: {request.method} /users/{path}")
    return forward_request(target)


@app.route("/orders/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/orders", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
def route_orders(path):
    """Orders don't need strangler pattern routing — just forward."""
    return forward_request(f"http://order_service:8000/orders/{path}")


@app.route("/")
def root():
    return {"message": "API Gateway running with strangler pattern"}
