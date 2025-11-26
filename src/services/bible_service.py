import os
from typing import Dict, List, Optional, Tuple

from src.providers.anthropic_provider import AnthropicProvider
from src.providers.cohere_provider import CohereProvider
from src.providers.hf_provider import HuggingFaceProvider
from src.providers.llm_base import DummyProvider, LLMProvider
from src.providers.ollama_provider import OllamaProvider
from src.providers.openai_provider import OpenAIProvider

try:
    from src.services.intertextuality_engine import IntertextualityEngine
except ImportError:  # noqa: PERF401
    IntertextualityEngine = None


class BibleService:
    def __init__(self):
        self.provider_name = os.getenv("LLM_PROVIDER", "OPENAI").lower()
        self.provider: LLMProvider = self._init_provider(self.provider_name)
        # Engine
        self.intertextuality_engine = None
        self.index_loaded = False
        if IntertextualityEngine is not None:
            try:
                self.intertextuality_engine = IntertextualityEngine()
                self.intertextuality_engine.load_index()
                self.index_loaded = self.intertextuality_engine.index is not None
                if not self.index_loaded:
                    print(
                        "Aviso: Índice FAISS não encontrado. "
                        "Execute 'python scripts/setup_corpus.py'."
                    )
            except Exception as e:  # noqa: BLE001
                print(
                    "Aviso: Motor de intertextualidade não pôde ser "
                    f"inicializado: {e}"
                )

        # Cache simples para resultados de similaridade
        self._cache_enabled = os.getenv("ENABLE_CACHE", "1") == "1"
        try:
            self._cache_max = int(os.getenv("CACHE_MAX_SIZE", "128"))
        except ValueError:
            self._cache_max = 128
        self._similarity_cache: Dict[Tuple[str, int], List[Tuple[Dict, float]]] = {}

    def _init_provider(self, name: str) -> LLMProvider:
        mapping = {
            "openai": OpenAIProvider,
            "anthropic": AnthropicProvider,
            "cohere": CohereProvider,
            "hf": HuggingFaceProvider,
            "huggingface": HuggingFaceProvider,
            "ollama": OllamaProvider,
        }
        provider_cls = mapping.get(name)
        if provider_cls is None:
            print(f"Aviso: Provider '{name}' desconhecido. Usando DummyProvider.")
            return DummyProvider()
        try:
            instance = provider_cls()
            return instance
        except Exception as e:  # noqa: BLE001
            print(f"Aviso: Falha ao inicializar provider '{name}': {e}")
            return DummyProvider()

    def _apply_temp_api_key(self, provider: LLMProvider, key: str):
        """Aplica temporáriamente uma chave de API ao provider."""
        provider_name = provider.name.lower()
        if provider_name == "openai" and hasattr(provider, "client"):
            try:
                from src.providers.openai_provider import OpenAI

                if OpenAI:
                    provider.client = OpenAI(api_key=key)
            except (ImportError, AttributeError):
                pass
        elif provider_name == "anthropic" and hasattr(provider, "client"):
            try:
                import anthropic

                provider.client = anthropic.Anthropic(api_key=key)
            except (ImportError, AttributeError):
                pass
        elif provider_name == "cohere" and hasattr(provider, "client"):
            try:
                import cohere

                provider.client = cohere.Client(key)
            except (ImportError, AttributeError):
                pass
        elif provider_name in ["huggingface", "hf"] and hasattr(provider, "token"):
            provider.token = key

    def get_bible_study_response(
        self,
        question: str,
        model: Optional[str] = None,
        provider_override: Optional[str] = None,
        model_override: Optional[str] = None,
        api_keys: Optional[Dict[str, Optional[str]]] = None,
    ) -> str:
        # Se provider override especificado, usa temporariamente
        provider_to_use = self.provider
        if provider_override:
            provider_to_use = self._init_provider(provider_override.lower())

        # Aplicar API keys temporárias se fornecidas
        if api_keys and provider_override:
            prov_name = provider_override.lower()
            if prov_name in api_keys and api_keys[prov_name]:
                self._apply_temp_api_key(provider_to_use, api_keys[prov_name])

        # Usar model_override se fornecido
        model_to_use = model_override or model

        system_prompt = (
            "Você é um assistente especializado em estudos bíblicos "
            "profundos e teologia. Responda às perguntas com embasamento "
            "bíblico, citando livro, capítulo e versículo quando possível. "
            "Mencione interpretações relevantes e responda em Português "
            "do Brasil.\n\n"
        )
        prompt = system_prompt + question
        try:
            return provider_to_use.generate(prompt, model=model_to_use)
        except Exception as e:  # noqa: BLE001
            return f"Erro ao gerar resposta: {e}"

    def find_similar_verses(
        self, query: str, top_k: int = 5
    ) -> List[Tuple[Dict, float]]:
        """
        Busca versos similares usando o motor de intertextualidade.

        Args:
            query: Texto ou referência para buscar
            top_k: Número de resultados

        Returns:
            Lista de tuplas (verso, score)
        """
        if self.intertextuality_engine is None or not self.index_loaded:
            return []
        key = (query, top_k)
        if self._cache_enabled and key in self._similarity_cache:
            return self._similarity_cache[key]
        try:
            results = self.intertextuality_engine.find_similar(query, top_k)
            if self._cache_enabled:
                if len(self._similarity_cache) >= self._cache_max:
                    # política simples: remove primeira chave inserida
                    first_key = next(iter(self._similarity_cache.keys()))
                    self._similarity_cache.pop(first_key, None)
                self._similarity_cache[key] = results
            return results
        except Exception as e:  # noqa: BLE001
            print(f"Erro na busca de similaridade: {e}")
            return []

    def explain_intertextual_links(
        self, verse_text: str, links: List[Tuple[Dict, float]]
    ) -> str:
        """
        Usa LLM para explicar os links intertextuais encontrados.

        Args:
            verse_text: Texto do verso original
            links: Lista de versos similares com scores

        Returns:
            Explicação gerada pelo LLM
        """
        if not links:
            return "Nenhum link intertextual encontrado ou LLM não configurado."

        # Monta contexto dos links
        links_context = "\n".join(
            [
                (
                    f"- {v['book']} {v['chapter']}:{v['verse']} "
                    f"(sim: {score:.2%})\n  {v['text'][:100]}..."
                )
                for v, score in links[:5]
            ]
        )

        prompt = (
            "Você é especialista em estudos bíblicos e intertextualidade.\n\n"
            "Verso analisado:\n" + verse_text + "\n\n"
            "Versos similares encontrados:\n" + links_context + "\n\n"
            "Explique conexões intertextuais entre o verso analisado "
            "e os versos similares. Considere: temas comuns, vocabulário "
            "compartilhado, paralelos teológicos, citações ou alusões. "
            "Seja conciso e acadêmico."
        )

        try:
            return self.get_bible_study_response(prompt)
        except Exception as e:  # noqa: BLE001
            return f"Erro ao gerar explicação: {str(e)}"
