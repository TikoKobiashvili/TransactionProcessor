import re
from unittest.mock import MagicMock, patch
from db import initialize_db


def normalize_sql_commands(command):
    """Normalize SQL commands for comparison."""
    # Remove leading and trailing whitespace
    command = command.strip()
    # Replace multiple spaces with a single space
    command = re.sub(r'\s+', ' ', command)
    return command


@patch('db.get_db_connection')
def test_initialize_db(mock_get_db_connection):
    # Create mock objects for connection and cursor
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Set up the mock connection to return the mock cursor
    mock_conn.cursor.return_value = mock_cursor
    mock_get_db_connection.return_value = mock_conn

    # Call the function to be tested
    initialize_db()

    # Assert the expected SQL commands were executed
    expected_commands = [
        "CREATE TABLE IF NOT EXISTS initial_data ( id SERIAL PRIMARY KEY, provider_name VARCHAR(255) NOT NULL, initial_value NUMERIC NOT NULL );",
        "CREATE TABLE IF NOT EXISTS historical_transactions ( id SERIAL PRIMARY KEY, provider_id INTEGER REFERENCES initial_data(id), transaction_value NUMERIC NOT NULL );",
        "INSERT INTO initial_data (provider_name, initial_value) VALUES ('Visa', 1000), ('Mastercard', 2000) ON CONFLICT DO NOTHING;",
        "INSERT INTO historical_transactions (provider_id, transaction_value) VALUES (1, 100), (1, 200), (2, -200) ON CONFLICT DO NOTHING;"
    ]

    # Check that the SQL commands were executed
    actual_commands = [call[0][0] for call in mock_cursor.execute.call_args_list]
    normalized_actual_commands = [normalize_sql_commands(cmd) for cmd in actual_commands]

    assert all(command in normalized_actual_commands for command in
               expected_commands), f"Expected commands: {expected_commands}, but got: {normalized_actual_commands}"

    # Verify that commit, close cursor, and close connection were called
    mock_conn.commit.assert_called_once()
    mock_cursor.close.assert_called_once()
    mock_conn.close.assert_called_once()
