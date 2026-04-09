from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.llm_service import generate_response
import time

router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    # Start total request timing
    request_start = time.time()
    print("\n===== NEW CHAT REQUEST =====")

    # Call LLM service
    answer, status = generate_response(request.query)

    # End total request timing
    request_end = time.time()
    total_time = request_end - request_start

    print(f"Total backend time: {total_time:.2f} seconds")
    print("===== REQUEST FINISHED =====\n")

    return {
        "answer": answer,
        "status": status
    }