import threading
import time
from unittest.mock import MagicMock, patch

import pytest
from keydb_updater import schedule_keydb_updates, update_keydb


@patch('keydb_updater.redis.StrictRedis')
@patch('keydb_updater.get_db_connection')
def test_update_keydb(mock_get_db_connection, mock_redis):
    # Mock Redis connection
    mock_redis_instance = MagicMock()
    mock_redis.return_value = mock_redis_instance

    # Mock Postgres connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Mock the get_db_connection to return a mocked connection
    mock_get_db_connection.return_value = mock_conn
    mock_conn.cursor.return_value = mock_cursor

    # Mock the initial_data result
    mock_cursor.fetchall.side_effect = [
        [(1, 'Visa', 1000), (2, 'Mastercard', 2000)],  # First fetchall call (initial_data)
        [(300,)],  # Second fetchone call (sum of transactions for Visa)
        [(-200,)],  # Third fetchone call (sum of transactions for Mastercard)
    ]

    # Mock the fetchone method to return sums for each provider
    mock_cursor.fetchone.side_effect = [
        (300,),  # for provider 1 (Visa)
        (-200,),  # for provider 2 (Mastercard)
    ]

    update_keydb()

    # Check that redis.set was called with correct values
    mock_redis_instance.set.assert_any_call('1_Visa', '1300')  # 1000 initial + 300 transaction
    mock_redis_instance.set.assert_any_call(
        '2_Mastercard', '1800'
    )  # 2000 initial - 200 transaction

    # Ensure the cursor and connection were closed
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()

    # Verify if queries were executed correctly
    assert mock_cursor.execute.call_count == 3


@pytest.fixture
def start_keydb_thread():
    """Fixture to start the KeyDB thread."""
    with patch('keydb_updater.update_keydb') as mock_update_keydb:
        keydb_thread = threading.Thread(
            target=schedule_keydb_updates, args=(1,)
        )  # 1-second interval for testing
        keydb_thread.daemon = True
        keydb_thread.start()
        # Give the thread a moment to start and execute a couple of updates
        time.sleep(2)
        yield mock_update_keydb
        keydb_thread.join(timeout=2)  # Wait for the thread to finish (if needed)


@patch('keydb_updater.get_db_connection')  # Mock the Postgres connection
def test_keydb_update_timing(mock_get_db_connection, start_keydb_thread):
    mock_update_keydb = start_keydb_thread

    # Record the times of calls
    call_times = []

    def update_keydb_wrapper():
        call_times.append(time.time())
        mock_update_keydb()

    with patch('keydb_updater.update_keydb', update_keydb_wrapper):
        start_keydb_thread()  # Make sure the thread is running and calling update_keydb

    # Calculate intervals
    intervals = [t2 - t1 for t1, t2 in zip(call_times, call_times[1:])]

    # Check that the intervals are within ±1 second of the expected interval
    # (1 second in this test)
    assert all(0.9 <= interval <= 1.1 for interval in intervals), f'Intervals: {intervals}'
