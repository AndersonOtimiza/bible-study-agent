from abc import ABC, abstractmethod
from typing import Optional


class LLMProvider(ABC):
    """Interface base para provedores LLM."""

    name: str = "base"

    @abstractmethod
    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        """Gera texto a partir de um prompt."""
        raise NotImplementedError


class DummyProvider(LLMProvider):
    """Provider fallback quando nenhum LLM real está configurado."""

    name = "dummy"

    def generate(self, prompt: str, model: Optional[str] = None) -> str:
        prefix = (
            "[DummyProvider] LLM não configurado. "
            "Configure variáveis de ambiente para usar um provedor real.\n"
        )
        return prefix + prompt[:200]
