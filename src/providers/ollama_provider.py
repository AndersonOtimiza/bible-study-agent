import os
from typing import Optional

import requests

from src.providers.llm_base import LLMProvider


class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self):
        self.host = os.getenv("OLLAMA_HOST", "http://localhost:11434")
        self.model = os.getenv("OLLAMA_MODEL", "llama3")

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        use_model = model or self.model
        payload = {"model": use_model, "prompt": prompt, "stream": False}
        try:
            r = requests.post(f"{self.host}/api/generate", json=payload, timeout=120)
            r.raise_for_status()
            data = r.json()
        except requests.ConnectionError:
            return (
                "❌ Ollama não está rodando. Para usar modelos locais:\n\n"
                "1. Instale Ollama: https://ollama.com/download\n"
                "2. Baixe um modelo: ollama pull llama3\n"
                "3. Inicie o servidor: ollama serve\n\n"
                "Ou escolha outro modelo de IA no seletor acima."
            )
        except requests.HTTPError as e:
            if "404" in str(e):
                return (
                    f"❌ Modelo '{use_model}' não encontrado no Ollama.\n\n"
                    f"Baixe o modelo: ollama pull {use_model}\n"
                    "Ou escolha outro modelo de IA."
                )
            return f"[OllamaProvider] Erro HTTP: {e}"
        except (requests.RequestException, ValueError) as e:
            return f"[OllamaProvider] Erro: {e}"
        if isinstance(data, dict) and "response" in data:
            return data["response"]
        return str(data)
