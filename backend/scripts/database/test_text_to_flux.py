from app.services.text_to_flux_service import answer_sensor_flux_question

questions = [
    "What was the average humidity?",
    "What was the highest temperature recorded?",
]

for question in questions:
    print("\n==============================")
    print("Question:", question)

    result = answer_sensor_flux_question(question)

    print("Status:", result["status"])
    print("Flux:", result["flux"])
    print("Answer:", result["answer"])