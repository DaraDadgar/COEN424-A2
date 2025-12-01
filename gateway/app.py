from flask import Flask, request, Response
import requests
import json
import random
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # folder where app.py lives
CONFIG_PATH = os.path.join(BASE_DIR, "gateway_config.json")

app = Flask(__name__)

def load_config():
    """Load routing config dynamically each request."""
    with open(CONFIG_PATH) as f:
        return json.load(f)

# 
def forward_request(target_url):
    """Forward request including JSON body when available."""

    try:
        json_body = request.get_json()
        use_json = True
    except:
        json_body = request.get_data()
        use_json = False

    if use_json:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key.lower() != "host"},
            params=request.args,
            json=json_body  # <-- forward as parsed JSON
        )
    else:
        response = requests.request(
            method=request.method,
            url=target_url,
            headers={key: value for key, value in request.headers if key.lower() != "host"},
            params=request.args,
            data=json_body   # fallback raw
        )

    return Response(response.content, status=response.status_code, headers=response.headers.items())


@app.route("/users/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
@app.route("/users", defaults={"path": ""}, methods=["GET", "POST", "PUT", "DELETE"])
def route_user_request(path):
    config = load_config()
    P = config.get("routing_percentage_v1", 0.5)

    # If the incoming JSON contains `age`, force routing to v2 so
    # new-schema requests always hit the v2 implementation. Parse JSON
    # robustly: try Flask's parser first, then fall back to raw body.
    body = request.get_json(silent=True)
    if body is None:
        raw = request.get_data(as_text=True) or ""
        try:
            body = json.loads(raw) if raw else {}
        except Exception:
            body = {}

    # Debug: print the parsed body so routing decisions can be observed.
    print(f"[GATEWAY] Parsed body for routing: {body}")

    if isinstance(body, dict) and "age" in body:
        target = f"{config['v2_url']}/users/{path}"
        version = "v2"
    else:
        # Decide routing based on probability P (strangler pattern)
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

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
