# user_service/events.py
import json
import os
import pika
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_USER = os.getenv("RABBITMQ_USERNAME", "guest")
RABBIT_PASS = os.getenv("RABBITMQ_PASSWORD", "guest")
RABBIT_EXCHANGE = os.getenv("RABBITMQ_EXCHANGE", "user_events")

def _get_connection():
    credentials = pika.PlainCredentials(RABBIT_USER, RABBIT_PASS)
    return pika.BlockingConnection(
        pika.ConnectionParameters(
            host=RABBIT_HOST,
            port=RABBIT_PORT,
            credentials=credentials
        )
    )

def publish_user_updated(user_id, field, value):
    event = {
        "type": "USER_UPDATED",
        "userId": user_id,
        "field": field,
        "value": value
    }

    try:
        connection = _get_connection()
        channel = connection.channel()

        # declare exchange (fanout or topic)
        channel.exchange_declare(exchange=RABBIT_EXCHANGE, exchange_type="fanout")

        channel.basic_publish(
            exchange=RABBIT_EXCHANGE,
            routing_key="",
            body=json.dumps(event).encode("utf-8")
        )

        print("[EVENT PUBLISHED]", json.dumps(event))

        connection.close()
        return True

    except Exception as e:
        print("[EVENT ERROR]", str(e))
        return False
