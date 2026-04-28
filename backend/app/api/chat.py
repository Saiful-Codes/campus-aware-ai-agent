import time
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response, generate_sensor_response
from app.services.routing_service import is_sensor_query
from app.services.sensor_service import get_latest_sensor_data
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
        "library", "campus", "building", "facility", "facilities","ask la trobe", "ask latrobe", "digital innovation hub",
        "student support", "student service", "student services",
        "medical centre", "career ready", "counselling", "accessibility", "library"
    ]

    return any(keyword in query for keyword in rag_keywords)


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")
    print(f"User query: {request.query}")

    # Sensor query branch
    if is_sensor_query(request.query):
        print("Detected SENSOR query. Using live IoT sensor flow...")

        sensor_data = get_latest_sensor_data()
        answer, status = generate_sensor_response(request.query, sensor_data)

        request_end = time.time()
        total_time = request_end - request_start

        print(f"Total backend time: {total_time:.2f} seconds")
        print("===== SENSOR REQUEST FINISHED =====\n")

        return {
            "answer": answer,
            "status": status,
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