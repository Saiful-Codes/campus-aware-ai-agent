from app.services.text_to_sql_service import answer_sensor_database_question

questions = [
    "What was the latest temperature?",
    "What was the average humidity?",
]

for question in questions:
    print("\n==============================")
    print("Question:", question)

    result = answer_sensor_database_question(question)

    print("Status:", result["status"])
    print("SQL:", result["sql"])
    print("Answer:", result["answer"])