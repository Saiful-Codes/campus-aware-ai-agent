import os
import fitz  # PyMuPDF

# function to load and extract text from all PDFs
def load_pdfs(folder_path):
    documents = []

    # loop through all files in the folder
    for file_name in os.listdir(folder_path):
        if file_name.endswith(".pdf"):
            file_path = os.path.join(folder_path, file_name)
            print(f"Processing: {file_name}")

            try:
                pdf = fitz.open(file_path)
                text = ""

                # extract text from each page
                for page in pdf:
                    text += page.get_text()

                documents.append({
                    "file_name": file_name,
                    "text": text
                })

            except Exception as e:
                print(f"Error reading {file_name}: {e}")

    return documents


# test run
if __name__ == "__main__":
    folder = os.path.join(os.path.dirname(__file__), "../../ragData")
    docs = load_pdfs(folder)

    print("\nTotal documents loaded:", len(docs))

    # print preview of first document
    if docs:
        print("\nSample text:\n")
        print(docs[0]["text"][:500])