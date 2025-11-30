import os
from flask import Flask
from user_service.routes import api
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix="/api")
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.environ.get("PORT", "8001"))
    app.run(host="0.0.0.0", port=port, debug=True)
