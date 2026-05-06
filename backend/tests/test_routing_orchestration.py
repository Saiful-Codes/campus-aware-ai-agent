import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

from app.services.routing_service import classify_query_intent


def test_conceptual_wellbeing_routes_general_conceptual():
    result = classify_query_intent("How can campuses improve student wellbeing?")
    assert result["intent"] == "general_conceptual"


def test_library_effectiveness_routes_general_conceptual():
    result = classify_query_intent("How do students usually use the library effectively?")
    assert result["intent"] == "general_conceptual"


def test_ai_chatbot_advantages_routes_general_conceptual():
    result = classify_query_intent("What are the advantages of AI chatbot for campuses?")
    assert result["intent"] == "general_conceptual"


def test_chisholm_rent_routes_exact_current_info():
    result = classify_query_intent("In Chisholm College how much is the weekly rent?")
    assert result["intent"] == "exact_current_info"


def test_exact_calendar_link_routes_exact_current_info():
    result = classify_query_intent("Give me the exact link for 2026 academic calendar")
    assert result["intent"] == "exact_current_info"


def test_sensor_average_temperature_routes_sensor_history():
    result = classify_query_intent("What is the average temperature this week?")
    assert result["intent"] == "sensor_history"


def test_current_temperature_routes_sensor_live():
    result = classify_query_intent("What is the current temperature?")
    assert result["intent"] == "sensor_live"


def test_specific_latrobe_policy_routes_rag_specific():
    result = classify_query_intent("Where is Ask La Trobe and what services does it provide?")
    assert result["intent"] == "rag_specific"
