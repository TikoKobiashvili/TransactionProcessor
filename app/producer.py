# The producer logic will send random
# transaction messages to the RabbitMQ queue every 10-40 seconds.

import json
import random
import time

from config import ORG_COUNT, logger
from rabbitmq import get_rabbitmq_channel, publish_message


def produce_messages():
    """Produce random messages and send them to RabbitMQ."""
    channel = get_rabbitmq_channel()
    if channel is None:
        return

    while True:
        message_id = random.randint(1, ORG_COUNT)
        message_value = random.randint(-1000, 1000)
        publish_message(channel, message_id, message_value)
        time.sleep(random.randint(10, 40))
