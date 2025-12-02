# user_service/events.py  (Compatible with consumer)

import json
import os
import pika
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_updates")


def publish_user_updated(user_id, field, value):
    event = {
        "type": "USER_UPDATED",
        "userId": user_id,
        "field": field,
        "value": value
    }

    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
        )
        channel = connection.channel()

        # MATCH CONSUMER — declare same queue
        channel.queue_declare(queue=RABBIT_QUEUE)

        channel.basic_publish(
            exchange="",                # IMPORTANT
            routing_key=RABBIT_QUEUE,   # MUST MATCH CONSUMER
            body=json.dumps(event)
        )

        print("[EVENT PUBLISHED]", event)
        connection.close()
        return True

    except Exception as e:
        print("[EVENT ERROR]", str(e))
        return False
