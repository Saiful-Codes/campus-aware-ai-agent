from sentence_transformers import SentenceTransformer
from rag_chunker import process_documents
from rag_loader import load_pdfs
import os


# load embedding model (only loads once)
model = SentenceTransformer('all-MiniLM-L6-v2')



#  function to create embeddings
def generate_embeddings(chunks):
    """
    Takes chunked text and converts each chunk into embedding vector
    """

    embedded_data = []

    for chunk in chunks:
        text = chunk["text"]

        # convert text → embedding vector
        embedding = model.encode(text)

        embedded_data.append({
            "file_name": chunk["file_name"],
            "text": text,
            "embedding": embedding
        })

    return embedded_data



#  test run
if __name__ == "__main__":
    # path to PDFs
    folder = os.path.join(os.path.dirname(__file__), "../../ragData")

    # Step 1
    docs = load_pdfs(folder)

    # Step 2
    chunks = process_documents(docs)

    print(f"\nTotal chunks: {len(chunks)}")

    # Step 3
    embedded_chunks = generate_embeddings(chunks)

    print("\nEmbeddings created:", len(embedded_chunks))

    # preview
    if embedded_chunks:
        print("\nSample embedding vector (first 10 values):\n")
        print(embedded_chunks[0]["embedding"][:10])