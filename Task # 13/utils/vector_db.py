import faiss

def create_faiss_index(embeddings):
    dimensions = embeddings.shape[1]
    faiss_index = faiss.IndexFlatL2(dimensions)   # Euclidean Distance
    faiss_index.add(embeddings)
    return faiss_index

def search(faiss_index, query_embedding, count=3):
    distance, indices = faiss_index.search(query_embedding, count)
    return distance, indices