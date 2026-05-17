import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

# Ensure import-time guard in rag_pipeline does not fail when .env is absent
# in test environments. The actual Gemini client is not exercised by these tests.
os.environ.setdefault("GEMINI_API_KEY", "test-key-for-concurrency-tests")

import app.rag.rag_pipeline as rag


def _make_mock_conn(execute_side_effect=None, fetchall_return=None):
    """Build a MagicMock conn whose `with conn.cursor() as cursor:` yields a mock cursor."""
    mock_cursor = MagicMock()

    if execute_side_effect is not None:
        mock_cursor.execute.side_effect = execute_side_effect
    if fetchall_return is not None:
        mock_cursor.fetchall.return_value = fetchall_return
    else:
        mock_cursor.fetchall.return_value = []

    mock_conn = MagicMock()
    # Support `with conn.cursor() as cursor:` protocol.
    mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
    mock_conn.cursor.return_value.__exit__.return_value = False
    return mock_conn, mock_cursor


def test_retrieve_opens_and_closes_connection_per_call():
    mock_conn_1, _ = _make_mock_conn()
    mock_conn_2, _ = _make_mock_conn()

    with patch(
        "app.rag.rag_pipeline.psycopg2.connect",
        side_effect=[mock_conn_1, mock_conn_2],
    ) as mock_connect:
        rag.retrieve_with_scores("first query")
        rag.retrieve_with_scores("second query")

    assert mock_connect.call_count == 2
    mock_conn_1.close.assert_called_once()
    mock_conn_2.close.assert_called_once()


def test_retrieve_closes_connection_on_error():
    mock_conn, _ = _make_mock_conn(execute_side_effect=RuntimeError("boom"))

    with patch("app.rag.rag_pipeline.psycopg2.connect", return_value=mock_conn):
        with pytest.raises(RuntimeError, match="boom"):
            rag.retrieve_with_scores("any query")

    mock_conn.close.assert_called_once()
