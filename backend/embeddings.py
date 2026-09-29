from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")  # downloads once, then cached

def embed(texts):
    return model.encode(texts).tolist()