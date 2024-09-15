# rabbitmq.py
import json
import time

import pika
from config import (
    QUEUE_NAME,
    RABBITMQ_HOST,
    RABBITMQ_PASSWORD,
    RABBITMQ_PORT,
    RABBITMQ_USER,
    logger,
)


def get_rabbitmq_channel():
    """Establish and return a RabbitMQ channel."""
    attempt_count = 0
    while attempt_count < 10:
        try:
            credentials = pika.PlainCredentials(RABBITMQ_USER, RABBITMQ_PASSWORD)
            connection = pika.BlockingConnection(
                pika.ConnectionParameters(
                    host=RABBITMQ_HOST, port=RABBITMQ_PORT, credentials=credentials
                )
            )
            channel = connection.channel()
            channel.queue_declare(queue=QUEUE_NAME, durable=True)
            logger.info('Connected to RabbitMQ')
            return channel
        except pika.exceptions.AMQPConnectionError:
            attempt_count += 1
            logger.warning(f'Reconnecting to RabbitMQ, attempt {attempt_count}')
            time.sleep(2)
    logger.error("Couldn't connect to RabbitMQ")
    return None


def publish_message(channel, id, value):
    """Publish a message to RabbitMQ."""
    message = {'id': id, 'value': value}
    channel.basic_publish(
        exchange='',
        routing_key=QUEUE_NAME,
        body=json.dumps(message),
        properties=pika.BasicProperties(
            delivery_mode=2,  # Make message persistent
        ),
    )
    logger.info(f'Sent message: {message}')
