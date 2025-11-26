from src.services.bible_service import BibleService


class DummyEngine:
    def __init__(self):
        self.index = True

    def find_similar(self, _query: str, _top_k: int):
        return [(
            {
                "book": "John",
                "chapter": 3,
                "verse": 16,
                "text": "Amor de Deus",
            },
            0.9,
        )]


def test_bible_service_without_index():
    service = BibleService()
    # Força estado de índice não carregado
    service.index_loaded = False
    results = service.find_similar_verses("amor", 3)
    assert results == []


def test_bible_service_with_dummy_engine_cache():
    service = BibleService()
    service.intertextuality_engine = DummyEngine()
    service.index_loaded = True
    first = service.find_similar_verses("amor", 3)
    second = service.find_similar_verses("amor", 3)
    assert first == second
    assert len(first) == 1


def test_bible_service_llm_dummy_provider():
    # Provider desconhecido força DummyProvider
    import os
    os.environ["LLM_PROVIDER"] = "desconhecido"
    service = BibleService()
    resp = service.get_bible_study_response("Explique João 3:16")
    assert "DummyProvider" in resp
