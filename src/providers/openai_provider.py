import os
from typing import Optional

from src.providers.llm_base import LLMProvider

try:
    from openai import OpenAI
except ImportError:
    OpenAI = None


class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self):
        api_key = os.getenv("OPENAI_API_KEY")
        self.client = OpenAI(api_key=api_key) if (api_key and OpenAI) else None

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.client:
            return (
                "❌ OpenAI não configurado.\n\n"
                "Adicione sua chave no arquivo .env:\n"
                "OPENAI_API_KEY=sk-sua-chave-aqui\n\n"
                "Ou escolha outro modelo de IA no seletor acima."
            )
        use_model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        try:
            resp = self.client.chat.completions.create(
                model=use_model,
                messages=[{"role": "user", "content": prompt}],
            )
            return resp.choices[0].message.content
        except Exception as e:
            error_msg = str(e)
            if (
                "not_authorized_invalid_key_type" in error_msg
                or "user keys" in error_msg.lower()
            ):
                return (
                    "❌ Erro de Autenticação OpenAI\n\n"
                    "Sua chave de API é uma 'user key', mas sua organização requer uma 'service account key' ou 'project key'.\n\n"
                    "**Como resolver:**\n"
                    "1. Acesse: https://platform.openai.com/api-keys\n"
                    "2. Crie uma nova chave de projeto (project key) ou service account\n"
                    "3. Configure a nova chave no modal de configuração (ícone ⚙️)\n\n"
                    f"Detalhes do erro: {error_msg}"
                )
            elif "401" in error_msg:
                return (
                    "❌ Chave de API OpenAI inválida ou sem permissão.\n\n"
                    "Verifique:\n"
                    "• A chave está correta (formato: sk-...)\n"
                    "• A chave tem permissões ativas\n"
                    "• Sua conta OpenAI tem créditos disponíveis\n\n"
                    f"Detalhes: {error_msg}"
                )
            else:
                return f"❌ Erro ao chamar OpenAI: {error_msg}"
