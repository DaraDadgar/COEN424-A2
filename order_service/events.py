# order_service/events.py

import pika, json, os, time
from order_service import repos
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv(), override=False)

# Host/port/queue configuration
RABBIT_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBIT_PORT = int(os.getenv("RABBITMQ_PORT", 5672))
RABBIT_QUEUE = os.getenv("RABBITMQ_QUEUE", "user_updates")

# Retry/backoff settings (seconds) - configurable via env
INITIAL_WAIT = int(os.getenv("RABBIT_INITIAL_WAIT", 0))
RETRY_DELAY = int(os.getenv("RABBIT_RETRY_DELAY", 5))


def start_consumer():
    """Start a consumer that waits/retries until RabbitMQ is available.

    Behavior:
    - Optionally wait INITIAL_WAIT seconds before the first attempt.
    - Try to connect; on failure wait RETRY_DELAY seconds and retry forever.
    - Once connected, consume messages until connection is lost, then retry.
    """
    if INITIAL_WAIT > 0:
        print(f"[OrderService] Waiting {INITIAL_WAIT}s before trying to connect to RabbitMQ...")
        time.sleep(INITIAL_WAIT)

    while True:
        connection = None
        try:
            print(f"[OrderService] Connecting to RabbitMQ at {RABBIT_HOST}:{RABBIT_PORT}...")
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
            )
            channel = connection.channel()
            channel.queue_declare(queue=RABBIT_QUEUE)

            def callback(ch, method, properties, body):
                try:
                    event = json.loads(body)
                    print("[OrderService] Received event:", event)
                    if event.get("type") == "USER_UPDATED":
                        user_id = event.get("userId")
                        field = event.get("field")
                        value = event.get("value")
                        repos.update_orders_by_user(user_id, field, value)
                except Exception as e:
                    print("[OrderService] Error handling event:", e)

            channel.basic_consume(
                queue=RABBIT_QUEUE,
                on_message_callback=callback,
                auto_ack=True,
            )

            print("[OrderService] Waiting for events...")
            channel.start_consuming()

        except Exception as e:
            print(f"[OrderService] RabbitMQ connection error: {e}. Retrying in {RETRY_DELAY}s...")
            try:
                if connection and not connection.is_closed:
                    connection.close()
            except Exception:
                pass
            time.sleep(RETRY_DELAY)
            continue
