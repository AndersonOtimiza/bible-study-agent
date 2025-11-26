import os
from typing import Optional

from src.providers.llm_base import LLMProvider

try:
    import cohere
except ImportError:
    cohere = None


class CohereProvider(LLMProvider):
    name = "cohere"

    def __init__(self):
        api_key = os.getenv("COHERE_API_KEY")
        self.client = cohere.Client(api_key) if (api_key and cohere) else None

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.client:
            return (
                "❌ Cohere não configurado.\n\n"
                "Adicione sua chave no arquivo .env:\n"
                "COHERE_API_KEY=sua-chave-aqui\n\n"
                "Ou escolha outro modelo de IA no seletor acima."
            )
        use_model = model or os.getenv("COHERE_MODEL", "command-xlarge-nightly")
        resp = self.client.generate(
            model=use_model,
            prompt=prompt,
            max_tokens=400,
        )
        return resp.text if hasattr(resp, "text") else str(resp)
