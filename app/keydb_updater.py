# The KeyDB updater fetches data from PostgreSQL and
# updates KeyDB every 60 seconds with the latest balances.

# keydb_updater.py

import redis
import time
from config import logger
from db import get_db_connection
from config import KEYDB_HOST, KEYDB_PORT


def update_keydb():
    """Update KeyDB with the latest values from the PostgreSQL database."""
    r = redis.StrictRedis(host=KEYDB_HOST, port=KEYDB_PORT, db=0)
    conn = get_db_connection()
    if conn is None:
        return

    cur = conn.cursor()

    # Read data from initial_data table
    cur.execute("""
        SELECT id, provider_name, initial_value FROM initial_data;
    """)
    providers = cur.fetchall()
    for provider_id, provider_name, initial_value in providers:
        # Query will return 0 instead of NULL when there are no transactions for the given provider_id.
        cur.execute("""
            SELECT COALESCE(SUM(transaction_value), 0) FROM historical_transactions WHERE provider_id = %s;
        """, (provider_id,))
        total_value = str(initial_value + cur.fetchone()[0])

        key = f"{provider_id}_{provider_name}"
        r.set(key, total_value)

        logger.info(f"Updated KeyDB: {key} = {total_value} at {time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime())}")

    cur.close()
    conn.close()


def schedule_keydb_updates(interval=60):
    """Schedule regular updates to KeyDB."""
    while True:
        update_keydb()
        time.sleep(interval)
