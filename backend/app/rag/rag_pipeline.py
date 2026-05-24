import os
import time
import psycopg2
from typing import Dict, List
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv

from app.services.llm_service import call_gemini_with_retry, GeminiCallError


# Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


# Embedding model
embed_model = SentenceTransformer("all-MiniLM-L6-v2")


def _open_pg_connection():
    return psycopg2.connect(
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
    )

RAG_SIMILARITY_HIGH = 0.75
RAG_SIMILARITY_MEDIUM = 0.62
RAG_SIMILARITY_THRESHOLD = 0.62


def retrieve(query, top_k=3):
    rows = retrieve_with_scores(query, top_k=top_k)
    return [row["content"] for row in rows]


def retrieve_with_scores(query: str, top_k: int = 5) -> List[Dict[str, float | str]]:
    print("Retrieving relevant PDF chunks from PostgreSQL...")

    query_embedding = embed_model.encode(query).tolist()

    conn = _open_pg_connection()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                """
                SELECT content, (embedding <-> %s::vector) AS distance
                FROM documents
                ORDER BY embedding <-> %s::vector
                LIMIT %s;
                """,
                (query_embedding, query_embedding, top_k),
            )

            results = cursor.fetchall()
    except Exception as e:
        print(f"RAG retrieval error: {e}")
        raise
    finally:
        conn.close()

    rows: List[Dict[str, float | str]] = []
    for row in results:
        content = row[0]
        distance = float(row[1]) if row[1] is not None else 999.0
        similarity = 1.0 / (1.0 + max(distance, 0.0))
        rows.append(
            {
                "content": content,
                "distance": distance,
                "similarity": similarity,
            }
        )

    print(f"Retrieved {len(rows)} relevant chunks from documents table.")

    return rows


def build_prompt(query, context_chunks):
    context = "\n\n".join(context_chunks)

    prompt = f"""
You are a smart, professional, and reliable campus assistant for La Trobe University Melbourne Campus.

Your task is to answer the user's question using ONLY the provided context.

Instructions:
1. Use only the information provided in the context below.
2. Do not make up, assume, infer, or speculate about any information.
3. Do not invent URLs, phone numbers, dates, fees, policies, locations, contacts, services, or procedures.
4. If the answer cannot be directly found or clearly supported in the provided context, respond EXACTLY with:
"I don't have enough information to answer that from the documents."
Do not provide general advice, assumptions, estimates, or external suggestions.
5. Keep answers clear, concise, natural, and easy for students to understand.
6. Structure answers neatly using short paragraphs or bullet points when appropriate.
7. If relevant, clearly mention building names, room numbers, services, contact details, or procedures found in the context.
8. Mention grid references only when they are directly useful for navigation or location-based questions.
9. Prioritise factual accuracy and grounded responses over completeness.

Context:
{context}

User Question:
{query}

Answer:
"""
    return prompt


def _rag_confidence_label(top_similarity: float, strong_chunks: int, total_chunks: int) -> str:
    if total_chunks == 0:
        return "low"

    if top_similarity >= RAG_SIMILARITY_HIGH and strong_chunks >= 1:
        return "high"

    if top_similarity >= RAG_SIMILARITY_MEDIUM and strong_chunks >= 1:
        return "medium"

    return "low"


def generate_answer_with_diagnostics(query: str, top_k: int = 5) -> Dict[str, object]:
    rag_start = time.time()
    print("Starting RAG pipeline with diagnostics...")

    rows = retrieve_with_scores(query, top_k=top_k)
    chunks = [row["content"] for row in rows]

    top_similarity = max([float(row["similarity"]) for row in rows], default=0.0)
    strong_chunks = sum(
        1
        for row in rows
        if float(row["similarity"]) >= RAG_SIMILARITY_THRESHOLD
    )
    confidence = _rag_confidence_label(top_similarity, strong_chunks, len(rows))

    if not chunks:
        print("No relevant document chunks found.")
        return {
            "answer": "I don't have enough information to answer that from the documents.",
            "context_chunks": [],
            "top_similarity": 0.0,
            "retrieved_chunk_count": 0,
            "chunks_above_threshold": 0,
            "confidence": "low",
            "runtime_seconds": round(time.time() - rag_start, 3),
        }

    print("Building RAG prompt with retrieved context...")
    prompt = build_prompt(query, chunks)

    print("Generating final RAG answer using Gemini...")
    try:
        text = call_gemini_with_retry(prompt, label="rag_answer")
    except GeminiCallError as e:
        print(f"RAG Gemini call failed terminally: {e}")
        text = ""

    total_time = time.time() - rag_start
    print(f"RAG Gemini response completed in {total_time:.2f} seconds.")

    answer = text if text else "I don't have enough information to answer that from the documents."
    return {
        "answer": answer,
        "context_chunks": chunks,
        "top_similarity": round(top_similarity, 4),
        "retrieved_chunk_count": len(rows),
        "chunks_above_threshold": strong_chunks,
        "confidence": confidence,
        "runtime_seconds": round(total_time, 3),
    }


def generate_answer(query):
    result = generate_answer_with_diagnostics(query)
    return str(result["answer"])