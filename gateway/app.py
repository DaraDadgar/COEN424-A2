from flask import Flask, request, Response
import requests
import json
import random
import os

app = Flask(__name__)


def load_config():
    """Load routing config dynamically each request.

    Uses the gateway directory so the app can be run from other working
    directories and still find its config file.
    """
    config_path = os.path.join(os.path.dirname(__file__), "gateway_config.json")
    with open(config_path, "r", encoding="utf-8") as f:
        return json.load(f)


def forward_request(target_url):
    """Generic forwarding helper to send request to target microservice.

    Sends the raw body (works for JSON and form-data) and forwards most
    headers except Host. Returns a Flask Response built from the
    downstream response.
    """
    # Copy headers, but remove Host (requests will set it)
    headers = {k: v for k, v in request.headers.items() if k.lower() != "host"}

    # Use raw body so we support JSON, form-data, files, etc.
    data = request.get_data()

    resp = requests.request(
        method=request.method,
        url=target_url,
        headers=headers,
        params=request.args,
        data=data,
        allow_redirects=False,
        timeout=10,
    )

    # Build response while filtering hop-by-hop headers
    excluded_headers = {
        "transfer-encoding",
        "connection",
        "keep-alive",
        "proxy-authenticate",
        "proxy-authorization",
        "te",
        "trailers",
        "upgrade",
    }

    response_headers = [(k, v) for k, v in resp.headers.items() if k.lower() not in excluded_headers]
    return Response(resp.content, status=resp.status_code, headers=response_headers)



@app.route("/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
@app.route("/users", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def route_user_request(path):
    config = load_config()

    # routing_percentage_v1 should be a float between 0.0 and 1.0 in the
    # config file. Validate and normalize it here so it's never hardcoded.
    try:
        P = float(config.get("routing_percentage_v1", 0.5))
    except (TypeError, ValueError):
        app.logger.warning("Invalid routing_percentage_v1 in config; defaulting to 0.5")
        P = 0.5

    if P < 0.0 or P > 1.0:
        app.logger.warning("routing_percentage_v1 out of range [0,1]; clamping")
        P = max(0.0, min(1.0, P))

    # Decide routing based on probability P
    if random.random() < P:
        # services expose APIs under /api/users
        target = f"{config['v1_url'].rstrip('/')}/api/users/{path}"
        version = "v1"
    else:
        target = f"{config['v2_url'].rstrip('/')}/api/users/{path}"
        version = "v2"

    app.logger.info(f"[GATEWAY] → {version.upper()} handling request: {request.method} /users/{path}")
    return forward_request(target)


@app.route("/orders/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/orders", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
def route_orders(path):
    """Orders don't need strangler pattern routing — just forward."""
    return forward_request(f"http://order_service:8000/orders/{path}")


@app.route("/")
def root():
    return {"message": "API Gateway running with strangler pattern"}
