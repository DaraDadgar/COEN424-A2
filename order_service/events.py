# order_service/events.py

import pika, json, os
from order_service import repos
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_updates")

def start_consumer():
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
    )
    channel = connection.channel()
    channel.queue_declare(queue=RABBIT_QUEUE)

    def callback(ch, method, properties, body):
        event = json.loads(body)
        print("[OrderService] Received event:", event)

        if event["type"] == "USER_UPDATED":
            user_id = event["userId"]
            field = event["field"]
            value = event["value"]
            repos.update_orders_by_user(user_id, field, value)

    channel.basic_consume(
        queue=RABBIT_QUEUE,
        on_message_callback=callback,
        auto_ack=True
    )

    print("[OrderService] Waiting for events...")
    channel.start_consuming()
