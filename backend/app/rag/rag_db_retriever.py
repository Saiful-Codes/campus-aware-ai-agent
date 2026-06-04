import psycopg2
import os
from sentence_transformers import SentenceTransformer
from dotenv import load_dotenv


#  Load environment variables
load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "../../../.env"))


#  load embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')



#  DB connection
conn = psycopg2.connect(
    dbname=os.getenv("DB_NAME"),
    user=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),  # keep empty or add if you set one
    host=os.getenv("DB_HOST"),
    port=os.getenv("DB_PORT") 
)


cursor = conn.cursor()



#  retrieve top chunks
def retrieve(query, top_k=3):
    """
    Takes user query and returns most relevant chunks from DB
    """

    # convert query -> embedding
    query_embedding = model.encode(query).tolist()

    cursor.execute(
        """
        SELECT file_name, content
        FROM documents
        ORDER BY embedding <-> %s::vector
        LIMIT %s;
        """,
        (query_embedding, top_k)
    )

    results = cursor.fetchall()
    return results



#  test run
if __name__ == "__main__":
    print("\nRAG DB Retrieval Ready. Type 'exit' to quit.\n")

    while True:
        query = input("You: ")

        if query.lower() in ["exit", "quit"]:
            break

        results = retrieve(query)

        print("\nTop Results:\n")

        for r in results:
            print("Source:", r[0])
            print(r[1][:300])
            print("-" * 50)