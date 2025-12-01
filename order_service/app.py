# order_service/app.py
import os
from flask import Flask
from order_service.routes import api
from dotenv import load_dotenv, find_dotenv
from threading import Thread
from order_service.events import start_consumer
load_dotenv(find_dotenv(), override=False)

def create_app():
    app = Flask(__name__)
    app.register_blueprint(api, url_prefix="/api")
    Thread(target=start_consumer, daemon=True).start()
    return app

if __name__ == "__main__":
    app = create_app()
    port = int(os.getenv("PORT", "8002"))
    app.run(host="0.0.0.0", port=port, debug=True)
