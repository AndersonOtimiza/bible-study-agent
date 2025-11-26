from fastapi.testclient import TestClient
from src.app import app

# Criar cliente de teste
client = TestClient(app)

def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("status") == "ok"

def test_root_serves_index():
    r = client.get("/")
    # FileResponse devolve 200 se arquivo existe
    assert r.status_code == 200

def test_find_similar_empty_index():
    # Como índice pode não estar carregado ainda, esperamos results vazio
    payload = {"query": "amor", "top_k": 2}
    r = client.post("/find-similar", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "amor"
    assert isinstance(data["results"], list)


def test_explain_links_handles_no_index():
    payload = {"query": "fé", "top_k": 2}
    r = client.post("/explain-links", json=payload)
    assert r.status_code == 200
    data = r.json()
    assert data["query"] == "fé"
    # Se não houver links, campo links deve existir
    assert "links" in data
    assert "explanation" in data
