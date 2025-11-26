import os
import importlib
import numpy as np
import types

# Monkeypatch SentenceTransformer before importing engine to avoid heavy model download
import sentence_transformers

class DummySentenceTransformer:
    def __init__(self, *args, **kwargs):
        pass

    def encode(self, texts, show_progress_bar=False, convert_to_numpy=True, normalize_embeddings=True):
        # Deterministic small embeddings: map index to simple vector
        base = []
        for i, _ in enumerate(texts):
            vec = np.zeros(3, dtype=float)
            vec[i % 3] = 1.0
            base.append(vec)
        arr = np.vstack(base)
        if normalize_embeddings:
            # Already one-hot
            pass
        return arr

# Replace original class
sentence_transformers.SentenceTransformer = DummySentenceTransformer

# Now import engine
from src.services.intertextuality_engine import IntertextualityEngine


def test_find_similar_basic():
    verses = [
        {"text": "amor de Deus", "book": "John", "chapter": 3, "verse": 16},
        {"text": "fé e esperança", "book": "Heb", "chapter": 11, "verse": 1},
        {"text": "amor ao próximo", "book": "Mt", "chapter": 22, "verse": 39},
    ]
    engine = IntertextualityEngine()
    engine.create_embeddings(verses)
    engine.build_index()

    results = engine.find_similar("amor", top_k=2)
    # Expect two results
    assert len(results) == 2
    # Ensure each result has expected keys
    for verse, score in results:
        assert "text" in verse
        assert isinstance(score, float)

    # The top result should contain word 'amor'
    assert "amor" in results[0][0]["text"].lower()
