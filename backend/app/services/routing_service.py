import re
from typing import Dict, List

YEAR_PATTERN = re.compile(r'\b(19|20)\d{2}\b')

MONTH_NAMES = [
    "january", "february", "march", "april", "may", "june",
    "july", "august", "september", "october", "november", "december",
]

SENSOR_KEYWORDS = [
    "temperature",
    "humidity",
    "pressure",
    "dew point",
    "sensor",
    "stuffy",
    "hot",
    "cold",
    "air",
    "weather",
    "reading",
    "environment",
]

SENSOR_HISTORY_KEYWORDS = [
    "average",
    "avg",
    "highest",
    "lowest",
    "maximum",
    "minimum",
    "max",
    "min",
    "count",
    "history",
    "historical",
    "trend",
    "between",
    "yesterday",
    "last hour",
    "last week",
    "last month",
    "over time",
    "show all",
    "all readings",
    "all sensor",
    "readings from",
]

SENSOR_LIVE_KEYWORDS = [
    "current",
    "latest",
    "now",
    "right now",
]

NAVIGATION_WHERE_PATTERNS = [
    "where is",
    "where's",
    "location of",
]

NAVIGATION_DIRECTIONS_PATTERNS = [
    "how do i get to",
    "how do i get from",
    "how to get to",
    "how to get from",
    "how to go from",
    "how to go to",
    "directions to",
    "directions from",
    "route to",
    "route from",
    "way to",
]

NAVIGATION_NEAREST_PATTERNS = [
    "nearest",
    "closest",
]

NAVIGATION_FACILITY_KEYWORDS = [
    "bathroom",
    "toilet",
    "restroom",
    "washroom",
    "library",
    "lab",
    "laboratory",
    "study space",
    "study",
]

GENERAL_CONCEPTUAL_PATTERNS = [
    "how can campuses improve",
    "how can campus improve",
    "how do students usually",
    "what are the advantages of",
    "what are the benefits of",
    "best way to",
    "best practices",
]

EXACT_CURRENT_INFO_KEYWORDS = [
    "exact link",
    "url",
    "website",
    "link",
    "calendar",
    "academic calendar",
    "current fee",
    "weekly rent",
    "rent",
    "how much",
    "price",
    "latest information",
    "current information",
]

RAG_SPECIFIC_KEYWORDS = [
    "ask la trobe",
    "glenn college",
    "menzies",
    "chisholm",
    "terraces",
    "ask latrobe",
    "studentonline",
    "usi",
    "enrolment",
    "digital innovation hub",
    "student services",
    "career ready",
    "medical centre",
    "orientation",
    "library hours",
    "building",
    "campus map",
]


def _contains_any(text: str, keywords: List[str]) -> bool:
    return any(keyword in text for keyword in keywords)


def is_sensor_history_query(message: str) -> bool:
    if not message:
        return False
    text = message.lower()
    if not _contains_any(text, SENSOR_KEYWORDS):
        return False
    if _contains_any(text, SENSOR_HISTORY_KEYWORDS):
        return True
    if YEAR_PATTERN.search(text):
        return True
    if _contains_any(text, MONTH_NAMES):
        return True
    return False


def is_sensor_live_query(message: str) -> bool:
    if not message:
        return False
    text = message.lower()
    if is_sensor_history_query(text):
        return False
    return _contains_any(text, SENSOR_KEYWORDS)


def is_sensor_query(message: str) -> bool:
    # Backward-compatible helper used by existing code paths.
    return is_sensor_live_query(message) or is_sensor_history_query(message)


def classify_query_intent(message: str) -> Dict[str, object]:
    text = (message or "").strip().lower()

    if not text:
        return {
            "intent": "normal_llm",
            "confidence": 0.5,
            "requiredTools": ["llm"],
            "reason": "Empty query defaults to normal LLM response.",
        }

    # CRITICAL: sensor routing wins over all other categories.
    if is_sensor_history_query(text):
        return {
            "intent": "sensor_history",
            "confidence": 0.98,
            "requiredTools": ["text_to_flux", "influxdb"],
            "reason": "Detected sensor + historical/aggregate wording.",
        }

    if is_sensor_live_query(text):
        return {
            "intent": "sensor_live",
            "confidence": 0.96,
            "requiredTools": ["sensor_api", "influxdb", "llm_format"],
            "reason": "Detected live/current sensor wording.",
        }

    if _contains_any(text, EXACT_CURRENT_INFO_KEYWORDS):
        return {
            "intent": "exact_current_info",
            "confidence": 0.88,
            "requiredTools": ["rag", "trusted_sources_guardrail"],
            "reason": "Detected exact/current/link/price request.",
        }

    if _contains_any(text, NAVIGATION_DIRECTIONS_PATTERNS):
        return {
            "intent": "navigation_directions",
            "confidence": 0.94,
            "requiredTools": ["postgres_navigation"],
            "reason": "Detected navigation directions phrasing.",
        }

    if _contains_any(text, NAVIGATION_NEAREST_PATTERNS) and _contains_any(
        text, NAVIGATION_FACILITY_KEYWORDS
    ):
        return {
            "intent": "navigation_nearest",
            "confidence": 0.94,
            "requiredTools": ["postgres_navigation"],
            "reason": "Detected nearest-facility navigation phrasing.",
        }

    if _contains_any(text, NAVIGATION_WHERE_PATTERNS):
        return {
            "intent": "navigation_where",
            "confidence": 0.9,
            "requiredTools": ["postgres_navigation"],
            "reason": "Detected where-is navigation phrasing.",
        }

    if _contains_any(text, GENERAL_CONCEPTUAL_PATTERNS):
        return {
            "intent": "general_conceptual",
            "confidence": 0.9,
            "requiredTools": ["llm", "rag_optional"],
            "reason": "Detected broad conceptual phrasing.",
        }

    if _contains_any(text, RAG_SPECIFIC_KEYWORDS):
        return {
            "intent": "rag_specific",
            "confidence": 0.82,
            "requiredTools": ["rag", "llm_fallback"],
            "reason": "Detected likely campus-policy or document-specific terms.",
        }

    return {
        "intent": "normal_llm",
        "confidence": 0.7,
        "requiredTools": ["llm"],
        "reason": "No strong rule match; using normal LLM path.",
    }