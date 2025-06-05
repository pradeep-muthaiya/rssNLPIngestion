from sentence_transformers import SentenceTransformer
from typing import List
import numpy as np
from app.core.config import settings

class NLPService:
    def __init__(self):
        self.model = SentenceTransformer(settings.MODEL_NAME)

    def extract_thesis(self, text: str) -> str:
        """
        Extract the main thesis statement from the text.
        This is a simplified version - you might want to use more sophisticated
        NLP techniques for better thesis extraction.
        """
        # Split text into sentences
        sentences = text.split('.')
        sentences = [s.strip() for s in sentences if len(s.strip()) > 20]  # Filter short sentences

        if not sentences:
            return ""

        # Get embeddings for all sentences
        embeddings = self.model.encode(sentences)

        # Calculate sentence importance scores (using mean of cosine similarities)
        scores = []
        for i, emb in enumerate(embeddings):
            similarities = np.dot(embeddings, emb) / (np.linalg.norm(embeddings, axis=1) * np.linalg.norm(emb))
            scores.append(np.mean(similarities))

        # Return the sentence with the highest score
        best_sentence_idx = np.argmax(scores)
        return sentences[best_sentence_idx]

    def calculate_similarity(self, thesis1: str, thesis2: str) -> float:
        """Calculate similarity between two thesis statements."""
        if not thesis1 or not thesis2:
            return 0.0

        emb1 = self.model.encode([thesis1])[0]
        emb2 = self.model.encode([thesis2])[0]

        similarity = np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2))
        return float(similarity) 