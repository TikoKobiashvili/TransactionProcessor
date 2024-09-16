import re

import pytest
from unittest.mock import MagicMock, patch
import json
from consumer import process_message


@pytest.fixture
def mock_channel():
    """Fixture for mocking the RabbitMQ channel."""
    return MagicMock()


@pytest.fixture
def mock_connection():
    """Fixture for mocking the database connection."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()
    mock_conn.cursor.return_value = mock_cursor
    return mock_conn, mock_cursor


def normalize_sql_commands(command):
    """Normalize SQL commands for comparison."""
    # Remove leading and trailing whitespace
    command = command.strip()
    # Replace multiple spaces with a single space
    command = re.sub(r'\s+', ' ', command)
    return command


@patch('consumer.get_db_connection')
def test_process_message_success(mock_get_db_connection, mock_channel, mock_connection):
    """Test processing a message successfully."""
    # Arrange
    mock_conn, mock_cursor = mock_connection
    mock_get_db_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = [1]  # Simulate provider exists
    mock_channel.basic_ack = MagicMock()

    body = json.dumps({'id': 1, 'value': 100})
    method = MagicMock(delivery_tag='tag')

    process_message(mock_channel, method, None, body)

    actual_calls = [normalize_sql_commands(call[0][0]) for call in mock_cursor.execute.call_args_list]

    expected_calls = [
        normalize_sql_commands("SELECT COUNT(*) FROM initial_data WHERE id = %s;"),
        normalize_sql_commands("INSERT INTO historical_transactions (provider_id, transaction_value) VALUES (%s, %s)")
    ]

    # Assert that expected SQL commands were executed
    for expected in expected_calls:
        assert any(expected in actual for actual in
                   actual_calls), f"Expected SQL command '{expected}' not found in actual calls."

    mock_conn.commit.assert_called_once()
    mock_channel.basic_ack.assert_called_once_with(delivery_tag='tag')
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()


@patch('consumer.get_db_connection')
def test_process_message_provider_not_found(mock_get_db_connection, mock_channel, mock_connection):
    """Test message rejection when provider ID is not found in the database."""
    mock_conn, mock_cursor = mock_connection
    mock_get_db_connection.return_value = mock_conn

    mock_cursor.fetchone.return_value = [0]
    mock_channel.basic_nack = MagicMock()

    body = json.dumps({'id': 1, 'value': 100})
    method = MagicMock(delivery_tag='tag')

    process_message(mock_channel, method, None, body)

    actual_calls = [normalize_sql_commands(call[0][0]) for call in mock_cursor.execute.call_args_list]
    expected_calls = [
        normalize_sql_commands("SELECT COUNT(*) FROM initial_data WHERE id = %s;")
    ]

    # Assert that expected SQL commands were executed
    for expected in expected_calls:
        assert any(expected in actual for actual in
                   actual_calls), f"Expected SQL command '{expected}' not found in actual calls."

    mock_channel.basic_nack.assert_called_once_with(delivery_tag='tag')
    mock_cursor.close.assert_called()
    mock_conn.close.assert_called()


@patch('consumer.get_db_connection')
def test_process_message_db_connection_failure(mock_get_db_connection, mock_channel):
    """Test message rejection when the database connection fails."""
    mock_get_db_connection.return_value = None
    mock_channel.basic_nack = MagicMock()

    body = json.dumps({'id': 1, 'value': 100})
    method = MagicMock(delivery_tag='tag')

    process_message(mock_channel, method, None, body)

    # Ensure that the message was rejected due to connection failure
    mock_channel.basic_nack.assert_called_once_with(delivery_tag='tag')
    mock_get_db_connection.assert_called_once()
