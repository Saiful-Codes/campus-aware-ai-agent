import time
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response, generate_sensor_response
from app.services.routing_service import is_sensor_query
from app.services.sensor_service import sync_latest_sensor_data
from app.services.sensor_db_service import get_latest_sensor_reading_from_db
from app.services.text_to_sql_service import answer_sensor_database_question
from app.rag.rag_pipeline import generate_answer

router = APIRouter()


def is_rag_query(query: str) -> bool:
    query = query.lower()

    rag_keywords = [
        "parking", "transport", "tram", "bus", "train", "entry",
        "sports", "gym", "swimming", "basketball", "stadium",
        "accommodation", "glenn college", "menzies", "chisholm", "terraces",
        "student services", "ask latrobe", "counselling", "medical centre",
        "career ready", "accessibility", "international",
        "orientation", "student id", "usi", "enrolment", "studentonline",
        "library", "campus", "building", "facility", "facilities",
        "ask la trobe", "ask latrobe", "digital innovation hub",
        "student support", "student service", "student services",
        "medical centre", "career ready", "counselling", "accessibility", "library"
    ]

    return any(keyword in query for keyword in rag_keywords)


def is_sensor_database_query(query: str) -> bool:
    query = query.lower()

    sensor_terms = [
        "temperature", "humidity", "pressure", "dew point",
        "sensor", "readings", "reading"
    ]

    database_terms = [
        "average", "avg", "highest", "lowest", "maximum", "minimum",
        "max", "min", "count", "how many", "stored", "recorded",
        "history", "historical", "yesterday", "last week", "last month",
        "between", "trend", "over time"
    ]

    return any(term in query for term in sensor_terms) and any(term in query for term in database_terms)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")
    print(f"User query: {request.query}")

    # Text-to-SQL branch for historical/analytical sensor questions
    if is_sensor_database_query(request.query):
        print("Detected SENSOR DATABASE query. Using Text-to-SQL flow...")

        try:
            result = answer_sensor_database_question(request.query)

            request_end = time.time()
            total_time = request_end - request_start

            print(f"Generated SQL: {result.get('sql')}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== TEXT-TO-SQL REQUEST FINISHED =====\n")

            return {
                "answer": result["answer"],
                "status": result["status"],
            }

        except Exception as e:
            request_end = time.time()
            total_time = request_end - request_start

            print(f"TEXT-TO-SQL ERROR: {e}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== TEXT-TO-SQL REQUEST FAILED =====\n")

            return {
                "answer": "Sorry, I could not query the sensor database right now.",
                "status": "text_to_sql_error",
            }

    # Live/latest sensor query branch
    if is_sensor_query(request.query):
        print("Detected SENSOR query. Using DB-backed IoT sensor flow...")

        try:
            sync_result = sync_latest_sensor_data()
            print(f"Sensor sync result: {sync_result}")

            sensor_data = get_latest_sensor_reading_from_db()
            answer, status = generate_sensor_response(request.query, sensor_data)

            request_end = time.time()
            total_time = request_end - request_start

            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== SENSOR REQUEST FINISHED =====\n")

            return {
                "answer": answer,
                "status": status,
            }

        except Exception as e:
            request_end = time.time()
            total_time = request_end - request_start

            print(f"SENSOR ERROR: {e}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== SENSOR REQUEST FAILED =====\n")

            return {
                "answer": "Sorry, I could not fetch the latest sensor data right now.",
                "status": "sensor_error",
            }

    # RAG query branch
    if is_rag_query(request.query):
        print("Detected RAG query. Using document retrieval flow...")

        try:
            answer = generate_answer(request.query)
            status = "rag_response"

            request_end = time.time()
            total_time = request_end - request_start

            print("RAG answer generated successfully.")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== RAG REQUEST FINISHED =====\n")

            return {
                "answer": answer,
                "status": status,
            }

        except Exception as e:
            request_end = time.time()
            total_time = request_end - request_start

            print(f"RAG ERROR: {e}")
            print(f"Total backend time: {total_time:.2f} seconds")
            print("===== RAG REQUEST FAILED =====\n")

            return {
                "answer": "Sorry, I could not answer from the uploaded documents right now.",
                "status": "rag_error",
            }

    # Normal LLM branch
    print("Detected NORMAL query. Using standard LLM flow...")

    answer, status = generate_response(request.query)

    request_end = time.time()
    total_time = request_end - request_start

    print(f"Total backend time: {total_time:.2f} seconds")
    print("===== NORMAL REQUEST FINISHED =====\n")

    return {
        "answer": answer,
        "status": status,
    }