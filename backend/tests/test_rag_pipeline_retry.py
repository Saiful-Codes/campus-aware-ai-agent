import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.rag.rag_pipeline as rag


NO_INFO_FALLBACK = "I don't have enough information to answer that."


def _stub_retrieve_with_chunks():
    """Patch retrieve_with_scores to return one strong chunk."""
    return patch(
        "app.rag.rag_pipeline.retrieve_with_scores",
        return_value=[
            {"content": "Library hours are 8am to 8pm.", "distance": 0.1, "similarity": 0.91},
        ],
    )


def _stub_retrieve_empty():
    return patch("app.rag.rag_pipeline.retrieve_with_scores", return_value=[])


def test_rag_uses_retry_helper_on_success():
    with _stub_retrieve_with_chunks(), \
         patch(
             "app.rag.rag_pipeline.call_gemini_with_retry",
             return_value="Library hours are 8am to 8pm.",
         ) as mock_helper:
        result = rag.generate_answer_with_diagnostics("when does the library open?")

    mock_helper.assert_called_once()
    assert result["answer"] == "Library hours are 8am to 8pm."
    assert result["context_chunks"] == ["Library hours are 8am to 8pm."]
    assert result["confidence"] in {"low", "medium", "high"}
    assert "runtime_seconds" in result


def test_rag_falls_back_gracefully_on_GeminiCallError():
    from app.services.llm_service import GeminiCallError

    with _stub_retrieve_with_chunks(), \
         patch(
             "app.rag.rag_pipeline.call_gemini_with_retry",
             side_effect=GeminiCallError("rag_answer call failed: 503"),
         ):
        result = rag.generate_answer_with_diagnostics("when does the library open?")

    assert result["answer"] == NO_INFO_FALLBACK
    # Other return-dict fields stay intact even on Gemini failure.
    assert result["context_chunks"] == ["Library hours are 8am to 8pm."]
    assert "confidence" in result
    assert "top_similarity" in result


def test_rag_returns_no_context_message_when_no_chunks():
    with _stub_retrieve_empty(), \
         patch("app.rag.rag_pipeline.call_gemini_with_retry") as mock_helper:
        result = rag.generate_answer_with_diagnostics("anything")

    mock_helper.assert_not_called()
    assert result["answer"] == "I don't have enough information to answer that from the documents."
    assert result["context_chunks"] == []
    assert result["confidence"] == "low"
