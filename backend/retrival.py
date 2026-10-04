from vectorstore import search

DISTANCE_THRESHOLD = 1.5

def retrieve_context(question: str, chat_id: str):
    results = search(question, chat_id=chat_id)
    docs = results["documents"][0]
    metas = results["metadatas"][0]
    distances = results["distances"][0]

    # Reject if the best match is worse than the threshold
    if not docs or distances[0] > DISTANCE_THRESHOLD:
        return None

    return list(zip(docs, metas, distances))