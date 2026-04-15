import time
from fastapi import APIRouter

from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response, generate_sensor_response
from app.services.routing_service import is_sensor_query
from app.services.sensor_service import get_latest_sensor_data

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")

    # Sensor query branch
    if is_sensor_query(request.query):
        print("Detected sensor query. Fetching live sensor data...")

        sensor_data = get_latest_sensor_data()
        answer, status = generate_sensor_response(request.query, sensor_data)

        request_end = time.time()
        total_time = request_end - request_start

        print(f"Total backend time: {total_time:.2f} seconds")
        print("===== REQUEST FINISHED =====\n")

        return {
            "answer": answer,
            "status": status,
        }

    # Normal LLM branch
    print("Detected normal query. Using standard LLM flow...")
    answer, status = generate_response(request.query)

    request_end = time.time()
    total_time = request_end - request_start

    print(f"Total backend time: {total_time:.2f} seconds")
    print("===== REQUEST FINISHED =====\n")

    return {
        "answer": answer,
        "status": status,
    }