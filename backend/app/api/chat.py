import time
import re
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import (
    generate_hybrid_response,
    generate_response,
    generate_sensor_response,
)
from app.services.routing_service import classify_query_intent
from app.services.influx_sensor_service import sync_latest_sensor_data_to_influx
from app.services.influx_query_service import get_latest_sensor_reading_from_influx
from app.services.text_to_flux_service import answer_sensor_flux_question
from app.rag.rag_pipeline import generate_answer_with_diagnostics

router = APIRouter()

def _extract_urls_from_chunks(chunks: list[str]) -> list[str]:
    urls: list[str] = []
    for chunk in chunks:
        for match in re.findall(r"https?://[^\s)\]}>]+", chunk):
            cleaned = match.rstrip(".,;")
            if cleaned not in urls:
                urls.append(cleaned)
    return urls


def _safe_exact_info_response(query: str, urls: list[str]) -> str:
    if urls:
        return (
            "I found a reference in the available documents that may help:\n"
            f"- {urls[0]}\n\n"
            "Please verify this is the current official page — document contents may not reflect the latest updates."
        )

    return (
        "I can't safely provide exact current information for this query. "
        "For accurate fees, links, dates, or official policies, please visit "
        "**latrobe.edu.au** directly or contact La Trobe student services."
    )


def _with_debug(
    request: ChatRequest,
    answer: str,
    status: str,
    debug_data: dict,
):
    if request.debug:
        return {
            "answer": answer,
            "status": status,
            "debug": debug_data,
        }

    return {
        "answer": answer,
        "status": status,
    }


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")
    print(f"User query: {request.query}")

    intent_data = classify_query_intent(request.query)
    intent = str(intent_data["intent"])

    debug_data = {
        "selectedRoute": intent,
        "intent": intent,
        "intentConfidence": intent_data["confidence"],
        "ragConfidence": None,
        "fallbackUsed": False,
        "sourcesUsed": [],
        "fallbackReason": "",
        "reason": intent_data["reason"],
    }

    # CRITICAL PRIORITY: sensor routes always execute before RAG or general LLM.
    if intent == "sensor_history":
        print("Detected SENSOR DATABASE query. Using Text-to-Flux flow...")

        try:
            result = answer_sensor_flux_question(request.query)
            debug_data["sourcesUsed"] = ["influxdb", "text_to_flux"]

            total_time = time.time() - request_start

            print(f"Generated Flux: {result.get('flux')}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== TEXT-TO-FLUX REQUEST FINISHED =====\n")

            return _with_debug(request, result["answer"], result["status"], debug_data)

        except Exception as e:
            total_time = time.time() - request_start

            print(f"TEXT-TO-FLUX ERROR: {e}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== TEXT-TO-FLUX REQUEST FAILED =====\n")

            return _with_debug(
                request,
                "Sorry, I could not query the InfluxDB sensor database right now.",
                "text_to_flux_error",
                debug_data,
            )

    # Live/latest sensor questions using live API sync + InfluxDB read.
    if intent == "sensor_live":
        print("Detected SENSOR query. Using InfluxDB-backed IoT sensor flow...")

        try:
            sync_result = sync_latest_sensor_data_to_influx()
            print(f"Influx sensor sync result: {sync_result}")

            sensor_data = get_latest_sensor_reading_from_influx()
            answer, status = generate_sensor_response(request.query, sensor_data)
            debug_data["sourcesUsed"] = ["sensor_api", "influxdb", "llm_format"]

            total_time = time.time() - request_start

            print(f"Latest InfluxDB sensor data: {sensor_data}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== SENSOR REQUEST FINISHED =====\n")

            return _with_debug(request, answer, status, debug_data)

        except Exception as e:
            total_time = time.time() - request_start

            print(f"SENSOR ERROR: {e}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== SENSOR REQUEST FAILED =====\n")

            return _with_debug(
                request,
                "Sorry, I could not fetch the latest sensor data right now.",
                "sensor_error",
                debug_data,
            )

    if intent == "exact_current_info":
        print("Detected exact/current info query. Applying trusted-source guardrail...")
        rag_result = generate_answer_with_diagnostics(request.query)
        urls = _extract_urls_from_chunks(rag_result.get("context_chunks", []))
        answer = _safe_exact_info_response(request.query, urls)

        debug_data["ragConfidence"] = rag_result.get("confidence")
        debug_data["sourcesUsed"] = ["rag"] if urls else ["trusted_sources_guardrail"]
        debug_data["fallbackUsed"] = not bool(urls)
        debug_data["fallbackReason"] = (
            "No direct trusted URL in retrieved context." if not urls else ""
        )

        total_time = time.time() - request_start
        print(f"Total backend time: {total_time:.2f} seconds")
        print("===== EXACT/CURRENT REQUEST FINISHED =====\n")

        status = "exact_info_from_rag" if urls else "exact_info_needs_trusted_source"
        return _with_debug(request, answer, status, debug_data)

    if intent in {"rag_specific", "general_conceptual"}:
        print("Detected RAG-capable query. Evaluating RAG confidence...")
        rag_result = generate_answer_with_diagnostics(request.query)
        rag_confidence = rag_result.get("confidence", "low")
        debug_data["ragConfidence"] = rag_confidence
        debug_data["sourcesUsed"] = ["rag"]

        if intent == "rag_specific" and rag_confidence == "high":
            total_time = time.time() - request_start
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== HIGH-CONFIDENCE RAG REQUEST FINISHED =====\n")
            return _with_debug(
                request,
                str(rag_result["answer"]),
                "rag_response",
                debug_data,
            )

        # RAG is supportive here: use snippets plus general LLM knowledge.
        hybrid_answer, hybrid_status = generate_hybrid_response(
            request.query,
            list(rag_result.get("context_chunks", [])),
        )

        debug_data["fallbackUsed"] = True
        debug_data["fallbackReason"] = (
            "RAG confidence was not high enough for strict document-only response."
        )
        debug_data["sourcesUsed"] = ["rag", "llm"]

        total_time = time.time() - request_start
        print(f"Total backend time: {total_time:.2f} seconds")
        print("===== HYBRID REQUEST FINISHED =====\n")
        return _with_debug(
            request,
            hybrid_answer,
            hybrid_status,
            debug_data,
        )

    # Normal LLM fallback
    print("Detected NORMAL query. Using standard LLM flow...")

    answer, status = generate_response(request.query)
    debug_data["sourcesUsed"] = ["llm"]

    total_time = time.time() - request_start

    print(f"Total backend time: {total_time:.2f} seconds")
    print("===== NORMAL REQUEST FINISHED =====\n")

    return _with_debug(request, answer, status, debug_data)