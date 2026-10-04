from text_extractor import extract_text
from chunking import chunk_text
from vectorstore import store_chunks

def ingest(file_path, filename=None, chat_id=None):
    filename = filename or file_path.split("/")[-1]
    pages = extract_text(file_path)
    chunks = chunk_text(pages) if pages else []

    if not chunks:
        return {
            "filename": filename,
            "pages": len(pages),
            "chunks": 0,
            "error": "No extractable text found — this may be a scanned/image-only or empty file."
        }

    # Pass chat_id down to the vector store to isolate data per chat
    store_chunks(chunks, filename, chat_id)
    return {"filename": filename, "pages": len(pages), "chunks": len(chunks)}