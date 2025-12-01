import os
from flask import Flask
from user_service_v2.routes import api
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix="/api")
    # Add a response header to help identify which service handled a request
    @app.after_request
    def add_version_header(response):
        response.headers["X-Service-Version"] = "v2"
        return response
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "8003"))
    app.run(host="0.0.0.0", port=port, debug=True)
