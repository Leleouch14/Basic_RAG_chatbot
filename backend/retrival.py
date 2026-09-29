from vectorstore import search

DISTANCE_THRESHOLD = 2.0

def retrieve_context(question: str):
    results = search(question)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    
    distances = results["distances"][0]

    if not docs or distances[0] > DISTANCE_THRESHOLD:
        return None
        
    return list(zip(docs, metas, distances))