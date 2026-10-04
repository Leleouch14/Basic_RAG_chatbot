import chromadb
from embeddings import embed

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("study_docs")

def store_chunks(chunks, source_filename, chat_id):
    texts = [c["text"] for c in chunks]
    vectors = embed(texts)
    collection.add(
        documents=texts,
        embeddings=vectors,
        metadatas=[{"source": source_filename, "page": c["page"], "chat_id": chat_id} for c in chunks],
        ids=[f"{chat_id}_{source_filename}_{i}" for i in range(len(chunks))]
    )

def search(question, chat_id, k=6):
    q_vector = embed([question])[0]
    return collection.query(query_embeddings=[q_vector], n_results=k, where={"chat_id": chat_id})

def delete_chat_chunks(chat_id):
    collection.delete(where={"chat_id": chat_id})