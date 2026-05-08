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


# --- Phase 2: routing bug fixes ---

def test_show_all_temperature_routes_sensor_history():
    result = classify_query_intent("Show all temperature readings")
    assert result["intent"] == "sensor_history"


def test_show_all_sensor_readings_routes_sensor_history():
    result = classify_query_intent("Show all sensor readings")
    assert result["intent"] == "sensor_history"


def test_humidity_in_1995_routes_sensor_history():
    result = classify_query_intent("What was the humidity in 1995?")
    assert result["intent"] == "sensor_history"


def test_temperature_in_2024_routes_sensor_history():
    result = classify_query_intent("What was the humidity in 2024?")
    assert result["intent"] == "sensor_history"


def test_temperature_in_january_routes_sensor_history():
    result = classify_query_intent("What was the temperature in January?")
    assert result["intent"] == "sensor_history"


def test_temperature_in_march_routes_sensor_history():
    result = classify_query_intent("Show humidity readings from March")
    assert result["intent"] == "sensor_history"


def test_temperature_readings_from_last_month_routes_sensor_history():
    result = classify_query_intent("Show temperature readings from last month")
    assert result["intent"] == "sensor_history"


def test_temperature_change_over_time_routes_sensor_history():
    result = classify_query_intent("How did temperature change over time?")
    assert result["intent"] == "sensor_history"


# --- Regression: live sensor queries must still route correctly ---

def test_latest_humidity_routes_sensor_live():
    result = classify_query_intent("What is the latest humidity?")
    assert result["intent"] == "sensor_live"


def test_temperature_right_now_routes_sensor_live():
    result = classify_query_intent("What is the temperature right now?")
    assert result["intent"] == "sensor_live"


def test_current_humidity_routes_sensor_live():
    result = classify_query_intent("What is the current humidity?")
    assert result["intent"] == "sensor_live"


# --- Phase 6: evaluation suite edge cases ---

def test_gibberish_routes_normal_llm():
    result = classify_query_intent("asdfghjkl")
    assert result["intent"] == "normal_llm"


def test_studentonline_routes_rag_specific():
    result = classify_query_intent("What is StudentOnline used for?")
    assert result["intent"] == "rag_specific"


def test_campus_map_routes_rag_specific():
    result = classify_query_intent("Where is the campus map?")
    assert result["intent"] == "rag_specific"


def test_benefits_of_green_spaces_routes_general_conceptual():
    result = classify_query_intent("What are the benefits of campus green spaces for student wellbeing?")
    assert result["intent"] == "general_conceptual"
