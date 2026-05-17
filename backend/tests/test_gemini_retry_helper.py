import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.services.llm_service as llm


def _response(text):
    r = MagicMock()
    r.text = text
    return r


def _fake_client(models_mock):
    fake = MagicMock()
    fake.models = models_mock
    return fake


def test_returns_text_on_first_attempt_success():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.return_value = _response("hello world")

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep") as mock_sleep:
        result = llm.call_gemini_with_retry("any prompt", label="test")

    assert result == "hello world"
    fake_client_models.generate_content.assert_called_once()
    mock_sleep.assert_not_called()


def test_retries_on_503_then_succeeds():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.side_effect = [
        Exception("503 Service Unavailable"),
        _response("recovered"),
    ]

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep") as mock_sleep:
        result = llm.call_gemini_with_retry("p", label="test")

    assert result == "recovered"
    assert fake_client_models.generate_content.call_count == 2
    mock_sleep.assert_called_once_with(2)


def test_retries_on_429_then_succeeds():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.side_effect = [
        Exception("429 Too Many Requests"),
        _response("ok"),
    ]

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep") as mock_sleep:
        result = llm.call_gemini_with_retry("p", label="test")

    assert result == "ok"
    mock_sleep.assert_called_once_with(2)


def test_non_retryable_raises_GeminiCallError_immediately():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.side_effect = Exception("400 Bad Request")

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep") as mock_sleep:
        with pytest.raises(llm.GeminiCallError):
            llm.call_gemini_with_retry("p", label="test")

    fake_client_models.generate_content.assert_called_once()
    mock_sleep.assert_not_called()


def test_exhausted_retries_raises_GeminiCallError():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.side_effect = Exception("503 Service Unavailable")

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep") as mock_sleep:
        with pytest.raises(llm.GeminiCallError):
            llm.call_gemini_with_retry("p", label="test", max_retries=2)

    assert fake_client_models.generate_content.call_count == 3
    assert mock_sleep.call_args_list == [
        ((2,), {}),
        ((4,), {}),
    ]


def test_empty_response_text_returns_empty_string():
    fake_client_models = MagicMock()
    fake_client_models.generate_content.return_value = _response("")

    with patch.object(llm, "client", _fake_client(fake_client_models)), \
         patch("app.services.llm_service.time.sleep"):
        result = llm.call_gemini_with_retry("p", label="test")

    assert result == ""
