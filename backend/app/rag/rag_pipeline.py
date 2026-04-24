import os
import psycopg2
from sentence_transformers import SentenceTransformer
import google.generativeai as genai
from dotenv import load_dotenv


#  Load environment variables
load_dotenv()


#  Get API key securely
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

genai.configure(api_key=api_key)


#  Use free Gemini model
model = genai.GenerativeModel("gemini-2.5-flash")


# 🔹 Embedding model
embed_model = SentenceTransformer('all-MiniLM-L6-v2')


#  PostgreSQL connection
conn = psycopg2.connect(
    dbname="rag_db",
    user="ifratbinhasanruhan",
    password="",  # keep empty or add if you set one
    host="localhost",
    port="5432"
)


cursor = conn.cursor()


#  Retrieve relevant chunks from DB
def retrieve(query, top_k=3):
    query_embedding = embed_model.encode(query).tolist()

    cursor.execute(
        """
        SELECT content
        FROM documents
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
        """,
        (query_embedding, top_k)
    )

    results = cursor.fetchall()
    return [r[0] for r in results]


# 🔹 Build strong prompt for Gemini
def build_prompt(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a smart and reliable campus assistant for La Trobe University.

Your task is to answer the user's question using ONLY the provided context.

Instructions:
- Use only the information from the context below.
- Do NOT make up or assume information.
- If the answer is not clearly available, say:
  "I don't have enough information to answer that."
- Keep the answer clear, concise, and helpful.
- If relevant, mention locations, buildings, or services clearly.
- Structure the answer in short sentences or bullet points if helpful.

Context:
{context}

User Question:
{query}

Answer:
"""
    return prompt


#  Generate final answer using Gemini
def generate_answer(query):
    chunks = retrieve(query)
    prompt = build_prompt(query, chunks)

    response = model.generate_content(prompt)

    return response.text


# 🔹 Test loop (terminal chatbot)
if __name__ == "__main__":
    print("\nRAG + Gemini Ready. Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        try:
            answer = generate_answer(query)

            print("\nAI:\n")
            print(answer)
            print("-" * 50)

        except Exception as e:
            print(f"\nError: {e}\n")