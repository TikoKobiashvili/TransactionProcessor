# consumer.py
# The consumer reads messages from RabbitMQ and writes
# the transaction data to the PostgreSQL historical_transactions table.

import json

from config import QUEUE_NAME, logger
from db import get_db_connection
from rabbitmq import get_rabbitmq_channel


def process_message(ch, method, properties, body):
    """Process a message from RabbitMQ."""
    message = json.loads(body)
    tx_id = message['id']
    tx_value = message['value']

    conn = get_db_connection()
    if conn is None:
        # If connection fails, reject the message
        ch.basic_nack(delivery_tag=method.delivery_tag)
        return

    cur = conn.cursor()
    try:
        # Check if the provider_id exists in the initial_data table
        cur.execute(
            """
            SELECT COUNT(*) FROM initial_data WHERE id = %s;
        """,
            (tx_id,),
        )
        provider_exists = cur.fetchone()[0] > 0  # Check if the provider exists

        if not provider_exists:
            # If provider_id does not exist, log an error and reject the message
            logger.error(f'Provider ID {tx_id} not found in initial_data. Message rejected.')
            ch.basic_nack(delivery_tag=method.delivery_tag)
            return

        cur.execute(
            """
            INSERT INTO historical_transactions (provider_id, transaction_value) VALUES (%s, %s)
        """,
            (tx_id, tx_value),
        )

        conn.commit()
        cur.close()
        conn.close()

        logger.info(f'Processed message: {message}')
        # successful processing
        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        # Logging exception that occurs during processing and rejecting the message
        logger.error(f'Error processing message: {e}')
        ch.basic_nack(delivery_tag=method.delivery_tag)
    finally:
        # To make sure that the cursor and connection are closed
        cur.close()
        conn.close()


def consume_messages():
    """Consume messages from RabbitMQ and process them."""
    channel = get_rabbitmq_channel()
    if channel is None:
        return

    # Configure the RabbitMQ consumer to use the process_message function
    channel.basic_consume(queue=QUEUE_NAME, on_message_callback=process_message, auto_ack=False)
    logger.info('Waiting for messages. To exit press CTRL+C')

    # Start consuming messages from RabbitMQ
    channel.start_consuming()
