import chromadb
from embeddings import embed

client = chromadb.PersistentClient(path="data/chroma_db")
collection = client.get_or_create_collection("study_docs")

def store_chunks(chunks, source_filename):
    vectors = embed(chunks)
    collection.add(
        documents=chunks,
        embeddings=vectors,
        metadatas=[{"source": source_filename} for _ in chunks],
        ids=[f"{source_filename}_{i}" for i in range(len(chunks))]
    )

def search(question, k=6):
    q_vector = embed([question])[0]
    return collection.query(query_embeddings=[q_vector], n_results=k)