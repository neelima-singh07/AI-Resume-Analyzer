from sentence_transformers import SentenceTransformer
model=SentenceTransformer('all-MiniLM-L6-v2')
def create_embedding(text):

    embedding = model.encode(text)

    return embedding
