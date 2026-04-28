import os
import time
import psycopg2
from sentence_transformers import SentenceTransformer
from google import genai
from dotenv import load_dotenv


# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))

# Get API key
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found. Check your .env file.")

client = genai.Client(api_key=api_key)


# Embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


# PostgreSQL connection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT"),
)

cursor = conn.cursor()


def retrieve(query, top_k=3):
    print("Retrieving relevant PDF chunks from PostgreSQL...")

    query_embedding = embed_model.encode(query).tolist()

    try:
        cursor.execute(
            """
            SELECT content
            FROM documents
            ORDER BY embedding <-> %s::vector
            LIMIT %s;
            """,
            (query_embedding, top_k),
        )

        results = cursor.fetchall()
        chunks = [r[0] for r in results]

        print(f"Retrieved {len(chunks)} relevant chunks from documents table.")

        return chunks

    except Exception as e:
        conn.rollback()
        print(f"RAG retrieval error: {e}")
        raise e


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


def generate_answer(query):
    rag_start = time.time()
    print("Starting RAG pipeline...")

    chunks = retrieve(query)

    if not chunks:
        print("No relevant document chunks found.")
        return "I don't have enough information to answer that from the documents."

    print("Building RAG prompt with retrieved context...")
    prompt = build_prompt(query, chunks)

    print("Generating final RAG answer using Gemini...")

    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=prompt,
    )

    total_time = time.time() - rag_start
    print(f"RAG Gemini response completed in {total_time:.2f} seconds.")

    if response.text:
        return response.text.strip()

    return "I don't have enough information to answer that."


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