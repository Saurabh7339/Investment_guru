from sentence_transformers import SentenceTransformer
import numpy as np

class EmbeddingService:
    def __init__(self, model_name='all-MiniLM-L6-v2'):
        self.model = SentenceTransformer(model_name)
    
    def get_embedding(self, text: str) -> list[float]:
        if not text.strip():
            return np.zeros(self.model.get_sentence_embedding_dimension()).tolist()
        embedding = self.model.encode(text, convert_to_tensor=False)
        return embedding.tolist()
    
    def get_embeddings_bulk(self, texts: list[str]) -> list[list[float]]:
        if not texts:
            return []
        embeddings = self.model.encode(texts, convert_to_tensor=False)
        return embeddings.tolist()