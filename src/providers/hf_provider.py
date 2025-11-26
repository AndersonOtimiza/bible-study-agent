import os
from typing import Optional

import requests

from src.providers.llm_base import LLMProvider


class HuggingFaceProvider(LLMProvider):
    name = "huggingface"

    def __init__(self):
        token = os.getenv("HF_API_TOKEN")
        self.token = token

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.token:
            return (
                "❌ Hugging Face não configurado.\n\n"
                "Adicione seu token no arquivo .env:\n"
                "HF_API_TOKEN=hf_sua-token-aqui\n\n"
                "Ou escolha outro modelo de IA no seletor acima."
            )
        use_model = model or os.getenv("HF_MODEL", "gpt2")
        headers = {"Authorization": f"Bearer {self.token}"}
        payload = {
            "inputs": prompt,
            "parameters": {"max_new_tokens": 300},
        }
        url = f"https://api-inference.huggingface.co/models/{use_model}"
        try:
            r = requests.post(url, headers=headers, json=payload, timeout=60)
            r.raise_for_status()
            data = r.json()
        except (requests.RequestException, ValueError) as e:
            return f"[HuggingFaceProvider] Erro: {e}"
        if isinstance(data, list) and data and "generated_text" in data[0]:
            return data[0]["generated_text"]
        if isinstance(data, dict) and "generated_text" in data:
            return data["generated_text"]
        return str(data)
