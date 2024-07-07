import pika
import json
import os
import logging
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

def callback(ch, method, properties, body):
    message = json.loads(body)
    logger.info(f" [x] Received {message}")

def main():
    rabbitmq_host = os.getenv('RABBITMQ_HOST', 'rabbitmq')
    queue_name = os.getenv('RABBITMQ_QUEUE', 'task_queue')

    try:
        create_connection(rabbitmq_host)
        channel = connection.channel()

        channel.queue_declare(queue=queue_name, durable=True)

        channel.basic_qos(prefetch_count=1)
        channel.basic_consume(queue=queue_name, on_message_callback=callback, auto_ack=True)

        logger.info(' [*] Waiting for messages. To exit press CTRL+C')
        channel.start_consuming()
    except Exception as e:
        logger.error(f"Error in consumer: {e}")
    finally:
        if connection:
            connection.close()

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    main()
