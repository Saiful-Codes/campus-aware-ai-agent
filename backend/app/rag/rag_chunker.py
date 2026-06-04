import os
import nltk
from nltk.tokenize import sent_tokenize
nltk.download('punkt_tab')



#  helper function to handle both sentence text and PDF-style broken text
def split_text(text):
    """
    Handles both normal sentences and structured PDF text.
    Falls back to line-based splitting if sentences are too few.
    """

    # try sentence-based splitting
    sentences = sent_tokenize(text)

    # if too few sentences → fallback to line splitting
    if len(sentences) < 50:
        lines = text.split("\n")
        sentences = [line.strip() for line in lines if line.strip()]

    return sentences




#  main chunking function
def chunk_text(text, chunk_size=80, overlap=20):
    """
    Splits text into chunks using smart splitting.

    chunk_size → approx number of words per chunk
    overlap → number of words repeated between chunks
    """

    sentences = split_text(text)

    chunks = []
    current_chunk = []
    current_length = 0

    for sentence in sentences:
        words = sentence.split()
        sentence_length = len(words)

        # if adding this sentence exceeds chunk size → save chunk
        if current_length + sentence_length > chunk_size:
            chunks.append(" ".join(current_chunk))

            # keep overlap words from previous chunk
            overlap_words = " ".join(current_chunk).split()[-overlap:]
            current_chunk = [" ".join(overlap_words)]
            current_length = len(overlap_words)

        current_chunk.append(sentence)
        current_length += sentence_length

    # add last chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks




#  process all documents
def process_documents(documents):
    """
    Takes list of documents from Step 1
    Returns list of chunks
    """

    all_chunks = []

    for doc in documents:
        text = doc["text"]
        file_name = doc["file_name"]

        print(f"Chunking: {file_name}")

        chunks = chunk_text(text)

        for chunk in chunks:
            all_chunks.append({
                "file_name": file_name,
                "text": chunk
            })

    return all_chunks




#  test run
if __name__ == "__main__":
    from rag_loader import load_pdfs

    # correct path to ragData folder
    folder = os.path.join(os.path.dirname(__file__), "../../ragData")

    docs = load_pdfs(folder)

    chunks = process_documents(docs)

    print("\nTotal chunks created:", len(chunks))

    # preview first chunk
    if chunks:
        print("\nSample chunk:\n")
        print(chunks[0]["text"][:500])