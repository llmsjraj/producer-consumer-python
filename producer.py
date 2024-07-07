import pika
import uuid
import json
import time
import os
import logging
from datetime import datetime, timezone
import signal
import sys
from tenacity import retry, wait_exponential, stop_after_attempt, before_sleep_log, after_log

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

connection = None

@retry(wait=wait_exponential(multiplier=1, min=4, max=10), 
       stop=stop_after_attempt(5),
       before_sleep=before_sleep_log(logger, logging.ERROR),
       after=after_log(logger, logging.INFO))
def create_connection(rabbitmq_host):
    global connection
    connection = pika.BlockingConnection(pika.ConnectionParameters(rabbitmq_host))
    return connection

def signal_handler(sig, frame):
    global connection
    logger.info("Signal received, shutting down...")
    if connection:
        connection.close()
    sys.exit(0)

def main(interval):
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    queue_name = os.getenv('RABBITMQ_QUEUE', 'task_queue')
    delivery_mode = int(os.getenv('RABBITMQ_DELIVERY_MODE', 2))  # Default to persistent

    try:
        create_connection(rabbitmq_host)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        while True:
            message_id = str(uuid.uuid4())
            created_on = datetime.now(timezone.utc).isoformat()
            message = {
                "message_id": message_id,
                "created_on": created_on
            }

            try:
                channel.basic_publish(
                    exchange='',
                    routing_key=queue_name,
                    body=json.dumps(message),
                    properties=pika.BasicProperties(
                        delivery_mode=delivery_mode,  # make message persistent
                    )
                )
                logger.info(f" [x] Sent {message}")
            except Exception as e:
                logger.error(f"Failed to send message: {e}")
            time.sleep(interval)
    except Exception as e:
        logger.error(f"Error in producer: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    INTERVAL = int(os.getenv('INTERVAL', 5))  # Default interval of 5 seconds
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main(INTERVAL)
