# main.py
# This script is responsible for starting the producer,
# consumer, and KeyDB updater in separate threads.
import logging
import threading

from consumer import consume_messages
from db import initialize_db
from keydb_updater import schedule_keydb_updates
from producer import produce_messages

# Set up logging
logging.basicConfig(level=logging.INFO)


def main():
    # Initialize the database
    initialize_db()

    # Start the KeyDB updater in a separate thread
    keydb_thread = threading.Thread(target=schedule_keydb_updates, args=(60,))
    keydb_thread.daemon = True
    keydb_thread.start()

    # Start the message consumer
    consumer_thread = threading.Thread(target=consume_messages)
    consumer_thread.daemon = True
    consumer_thread.start()

    # Start the message producer
    produce_messages()


if __name__ == '__main__':
    main()
