import psycopg2
import os

from rag_loader import load_pdfs
from rag_chunker import process_documents
from rag_embedder import generate_embeddings



#  DB connection (UPDATE password if needed)
conn = psycopg2.connect(
    dbname="rag_db",
    user="ifratbinhasanruhan",   # actual username from psql
    password="",                 # try empty first (or put your password if set)
    host="localhost",
    port="5432"
)


cursor = conn.cursor()



#  clear table (useful during testing)
def clear_table():
    cursor.execute("DELETE FROM documents;")
    conn.commit()
    print("Table cleared.")



#  store embeddings
def store_embeddings(embedded_chunks):
    for item in embedded_chunks:
        cursor.execute(
            """
            INSERT INTO documents (file_name, content, embedding)
            VALUES (%s, %s, %s)
            """,
            (
                item["file_name"],
                item["text"],
                item["embedding"].tolist()  # convert numpy -> list
            )
        )

    conn.commit()
    print(f"Stored {len(embedded_chunks)} embeddings successfully!")


#  main run
if __name__ == "__main__":
    folder = os.path.join(os.path.dirname(__file__), "../../ragData")

    # Step 1
    print("Loading PDFs...")
    docs = load_pdfs(folder)

    # Step 2
    print("Chunking documents...")
    chunks = process_documents(docs)

    # Step 3
    print("Generating embeddings...")
    embedded_chunks = generate_embeddings(chunks)

    # Step 4
    print("Storing in database...")
    clear_table()  # optional
    store_embeddings(embedded_chunks)

    print("done!")