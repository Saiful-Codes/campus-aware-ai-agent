from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
from app.services.routing_service import is_sensor_query
from app.services.sensor_service import get_latest_sensor_data, build_sensor_response
import time

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Start total request timing
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")

    # Sensor query branch
    if is_sensor_query(request.query):
        sensor_data = get_latest_sensor_data()
        sensor_reply = build_sensor_response(request.query, sensor_data)

        # End total request timing
        request_end = time.time()
        total_time = request_end - request_start

        print(f"Total backend time: {total_time:.2f} seconds")
        print("===== REQUEST FINISHED =====\n")

        return {
            "answer": sensor_reply,
            "status": "sensor_response",
        }

    # Normal LLM branch
    answer, status = generate_response(request.query)

    # End total request timing
    request_end = time.time()
    total_time = request_end - request_start

    print(f"Total backend time: {total_time:.2f} seconds")
    print("===== REQUEST FINISHED =====\n")

    return {
        "answer": answer,
        "status": status,
    }