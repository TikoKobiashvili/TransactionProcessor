# config.py

import os
from dotenv import load_dotenv
import logging

# Load environment variables from .env file
load_dotenv()

# Database Configuration
DB_NAME = os.getenv("POSTGRES_DB", "fxc")
DB_USER = os.getenv("POSTGRES_USER", "user")
DB_PASSWORD = os.getenv("POSTGRES_PASSWORD", "password")
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", 5432)

# RabbitMQ Configuration
RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "rabbitmq")
RABBITMQ_PORT = int(os.getenv("RABBITMQ_PORT", "5672"))
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "user")
RABBITMQ_PASSWORD = os.getenv("RABBITMQ_PASSWORD", "password")
QUEUE_NAME = os.getenv("RABBITMQ_QUEUE", "incoming_transactions")

# KeyDB
KEYDB_HOST = os.getenv("KEYDB_HOST", "keydb")
KEYDB_PORT = os.getenv("KEYDB_PORT", "6379")

# Other Configurations
ORG_COUNT = int(os.getenv("ORG_COUNT"))

# Logger configuration
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)
