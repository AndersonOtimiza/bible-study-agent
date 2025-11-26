import os
from typing import Optional

from src.providers.llm_base import LLMProvider

try:
    import anthropic
except ImportError:
    anthropic = None


class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if anthropic and api_key:
            try:
                self.client = anthropic.Client(api_key=api_key)
            except (AttributeError, TypeError):
                self.client = anthropic.Anthropic(api_key=api_key)
        else:
            self.client = None

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        if not self.client:
            return (
                "❌ Anthropic (Claude) não configurado.\n\n"
                "Adicione sua chave no arquivo .env:\n"
                "ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui\n\n"
                "Ou escolha outro modelo de IA no seletor acima."
            )
        use_model = model or os.getenv("ANTHROPIC_MODEL", "claude-2.1")
        HUMAN_PROMPT = getattr(anthropic, "HUMAN_PROMPT", "Human:")
        AI_PROMPT = getattr(anthropic, "AI_PROMPT", "Assistant:")
        combined = f"{HUMAN_PROMPT}\n{prompt}\n{AI_PROMPT}"
        resp = self.client.completions.create(
            model=use_model,
            prompt=combined,
            max_tokens_to_sample=800,
        )
        if isinstance(resp, dict) and "completion" in resp:
            return resp["completion"]
        return getattr(resp, "completion", str(resp))
