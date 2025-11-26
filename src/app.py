import os

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI, Header
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from src.services.bible_service import BibleService

# Carregar variáveis de ambiente
load_dotenv()

app = FastAPI(title="AN Agent - Bible Study One Web")

# Configurar serviço
bible_service = BibleService()


# Modelos de dados para requisições
class QuestionRequest(BaseModel):
    question: str
    provider: str | None = None


class SimilarityRequest(BaseModel):
    query: str
    top_k: int = 5


# Montar arquivos estáticos
app.mount("/static", StaticFiles(directory="src/static"), name="static")


@app.get("/")
def read_root():
    return FileResponse("src/static/index.html")


@app.post("/ask")
def ask_bible_question(
    request: QuestionRequest,
    x_openai_key: str | None = Header(None),
    x_anthropic_key: str | None = Header(None),
    x_cohere_key: str | None = Header(None),
    x_hf_token: str | None = Header(None),
):
    # Extrair provider e modelo (ex: "ollama:llama3" -> provider="ollama", model="llama3")
    provider_override = request.provider
    model_override = None
    if provider_override and ":" in provider_override:
        provider_override, model_override = provider_override.split(":", 1)

    # Passar chaves de API via override temporário
    api_keys = {
        "openai": x_openai_key,
        "anthropic": x_anthropic_key,
        "cohere": x_cohere_key,
        "huggingface": x_hf_token,
    }

    response = bible_service.get_bible_study_response(
        request.question,
        provider_override=provider_override,
        model_override=model_override,
        api_keys=api_keys,
    )
    return {"response": response}


@app.post("/find-similar")
def find_similar_verses(request: SimilarityRequest):
    """Encontra versos similares usando busca semântica."""
    results = bible_service.find_similar_verses(request.query, request.top_k)

    return {
        "query": request.query,
        "results": [
            {
                "book": verse["book"],
                "chapter": verse["chapter"],
                "verse": verse["verse"],
                "text": verse["text"],
                "similarity_score": float(score),
            }
            for verse, score in results
        ],
    }


@app.post("/explain-links")
def explain_intertextual_links(request: SimilarityRequest):
    """Encontra versos similares e explica as conexões intertextuais."""
    links = bible_service.find_similar_verses(request.query, request.top_k)

    if not links:
        return {
            "query": request.query,
            "links": [],
            "explanation": "Nenhuma conexão intertextual encontrada. Certifique-se de que o índice foi construído.",
        }

    explanation = bible_service.explain_intertextual_links(request.query, links)

    return {
        "query": request.query,
        "links": [
            {
                "book": verse["book"],
                "chapter": verse["chapter"],
                "verse": verse["verse"],
                "text": verse["text"][:100] + "...",
                "similarity_score": float(score),
            }
            for verse, score in links
        ],
        "explanation": explanation,
    }


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/gpu/status")
def get_gpu_status():
    """Retorna o status atual da GPU."""
    return bible_service.engine.get_device_info()


@app.post("/gpu/set")
def set_gpu_device(device: str):
    """Altera o device (cpu/cuda) em runtime."""
    result = bible_service.engine.set_device(device)
    return result


@app.post("/gpu/toggle")
def toggle_gpu():
    """Alterna entre CPU e GPU automaticamente."""
    current = bible_service.engine.device
    new_device = "cpu" if current == "cuda" else "cuda"
    result = bible_service.engine.set_device(new_device)
    return result


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
