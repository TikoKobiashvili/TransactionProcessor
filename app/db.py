# This module provides a helper function to establish a PostgreSQL connection.

import psycopg2
from config import DB_NAME, DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, logger
import time


def get_db_connection():
    """Establish and return a connection to the PostgreSQL database."""

    # Establish a connection to Postgres
    attempt_count = 0
    while attempt_count < 10:
        try:
            # Connection details
            conn = psycopg2.connect(
                dbname=DB_NAME,
                user=DB_USER,
                password=DB_PASSWORD,
                host=DB_HOST,
                port=DB_PORT
            )
            logger.info("Connected to PostgreSQL")
            return conn
        except psycopg2.OperationalError:
            attempt_count += 1
            logger.warning(f"Reconnecting to Postgres, attempt {attempt_count}")
            time.sleep(2)
    logger.error("Couldn't connect to PostgreSQL")
    return None


def initialize_db():
    """Initialize the database by creating tables and inserting initial data."""
    conn = get_db_connection()
    if conn is None:
        return

    # Creating a cursor object to interact with the database
    cur = conn.cursor()

    # Create the initial_data table only if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS initial_data (
            id SERIAL PRIMARY KEY,
            provider_name VARCHAR(255) NOT NULL,
            initial_value NUMERIC NOT NULL
        );
    """)

    # Create the historical_transactions table only if it does not exist
    cur.execute("""
        CREATE TABLE IF NOT EXISTS historical_transactions (
            id SERIAL PRIMARY KEY,
            provider_id INTEGER REFERENCES initial_data(id),
            transaction_value NUMERIC NOT NULL
        );
    """)

    # Insert data into initial_data table
    cur.execute("""
        INSERT INTO initial_data (provider_name, initial_value) VALUES
        ('Visa', 1000),
        ('Mastercard', 2000)
        ON CONFLICT DO NOTHING;
    """)

    # Insert data into historical_transactions table
    cur.execute("""
        INSERT INTO historical_transactions (provider_id, transaction_value) VALUES
        (1, 100),
        (1, 200),
        (2, -200)
        ON CONFLICT DO NOTHING;
    """)

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cur.close()
    conn.close()
    logger.info("Database initialization complete")
