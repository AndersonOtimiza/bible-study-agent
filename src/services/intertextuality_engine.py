import json
import os
from typing import Dict, List, Tuple

import faiss
import numpy as np
import torch
from sentence_transformers import SentenceTransformer


class IntertextualityEngine:
    """Motor de busca semântica para detectar intertextualidade bíblica."""

    def __init__(self, model_name: str = "paraphrase-multilingual-mpnet-base-v2"):
        """
        Inicializa o motor com um modelo de embeddings.

        Args:
            model_name: Nome do modelo Sentence Transformers
                       (default: multilíngue incluindo grego/hebraico)
        """
        print(f"Carregando modelo {model_name}...")
        self.model_name = model_name
        self._init_device()
        self.index = None
        self.verses = []
        self.embeddings = None

    def _init_device(self):
        """Inicializa ou reinicializa o device baseado nas variáveis de ambiente."""
        # Verificar configuração de device
        torch_device = os.getenv("TORCH_DEVICE", "auto").lower()
        gpu_enabled = os.getenv("USE_GPU", "1") == "1"

        if torch_device == "cpu" or not gpu_enabled:
            self.device = "cpu"
        elif torch_device == "cuda":
            self.device = "cuda" if torch.cuda.is_available() else "cpu"
        else:  # auto
            self.device = "cuda" if torch.cuda.is_available() else "cpu"

        # Carregar modelo no device apropriado
        if hasattr(self, "model"):
            # Recarregar modelo em device diferente
            self.model = SentenceTransformer(self.model_name, device=self.device)
        else:
            self.model = SentenceTransformer(self.model_name, device=self.device)

        if self.device == "cuda":
            gpu_name = torch.cuda.get_device_name(0)
            gpu_memory = torch.cuda.get_device_properties(0).total_memory / 1024**3
            print(f"✓ Modelo carregado na GPU: {gpu_name}")
            print(f"  • Memória GPU: {gpu_memory:.2f} GB")
            print(f"  • CUDA Version: {torch.version.cuda}")
        else:
            print("✓ Modelo carregado em CPU")
            print("  💡 Para usar GPU: execute scripts/check_gpu.py")

    def set_device(self, device: str) -> dict:
        """
        Altera o device (CPU/GPU) em runtime.

        Args:
            device: 'cpu' ou 'cuda'

        Returns:
            Dict com status da mudança
        """
        if device not in ["cpu", "cuda"]:
            return {"status": "error", "message": "Device deve ser 'cpu' ou 'cuda'"}

        if device == "cuda" and not torch.cuda.is_available():
            return {"status": "error", "message": "CUDA não disponível neste sistema"}

        old_device = self.device
        os.environ["USE_GPU"] = "1" if device == "cuda" else "0"
        os.environ["TORCH_DEVICE"] = device

        self._init_device()

        return {
            "status": "success",
            "message": f"Device alterado de {old_device} para {self.device}",
            "old_device": old_device,
            "new_device": self.device,
        }

    def get_device_info(self) -> dict:
        """Retorna informações sobre o device atual."""
        info = {
            "device": self.device,
            "cuda_available": torch.cuda.is_available(),
        }

        if torch.cuda.is_available():
            info["gpu_name"] = torch.cuda.get_device_name(0)
            info["gpu_memory_total"] = (
                torch.cuda.get_device_properties(0).total_memory / 1024**3
            )
            info["gpu_memory_allocated"] = torch.cuda.memory_allocated(0) / 1024**3
            info["gpu_memory_reserved"] = torch.cuda.memory_reserved(0) / 1024**3
            info["cuda_version"] = torch.version.cuda

        return info

    def create_embeddings(self, verses: List[Dict]) -> np.ndarray:
        """
        Cria embeddings para todos os versos.

        Args:
            verses: Lista de dicts ('text','book','chapter','verse')

        Returns:
            Array numpy com embeddings
        """
        self.verses = verses
        texts = [v["text"].strip() for v in verses]

        print(f"Gerando embeddings para {len(texts)} versos...")
        self.embeddings = self.model.encode(
            texts,
            show_progress_bar=True,
            convert_to_numpy=True,
            normalize_embeddings=True,  # Normaliza para cosine similarity
        )

        return self.embeddings

    def build_index(self, embeddings: np.ndarray = None):
        """
        Constrói índice FAISS para busca rápida.

        Args:
            embeddings: Array de embeddings (usa self.embeddings se None)
        """
        if embeddings is None:
            embeddings = self.embeddings

        if embeddings is None:
            raise ValueError(
                ("Embeddings não encontrados. Execute " "create_embeddings primeiro.")
            )

        dimension = embeddings.shape[1]
        num_vectors = embeddings.shape[0]
        print(
            f"Construindo índice FAISS (dim={dimension}, " f"{num_vectors:,} versos)..."
        )

        # IndexFlatIP: Inner Product (cosine similarity)
        self.index = faiss.IndexFlatIP(dimension)

        # Adiciona embeddings em batches para feedback visual
        batch_size = 1000
        for i in range(0, num_vectors, batch_size):
            end = min(i + batch_size, num_vectors)
            self.index.add(embeddings[i:end].astype("float32"))
            pct = (end / num_vectors) * 100
            print(f"  Indexando: {end:,}/{num_vectors:,} ({pct:.1f}%)", end="\r")

        print(f"\n✓ Índice construído com {self.index.ntotal:,} versos")
        # Opcional: mover índice para GPU se disponível e solicitado
        try:
            if os.getenv("USE_FAISS_GPU", "0") == "1" and hasattr(
                faiss, "StandardGpuResources"
            ):
                num_gpus = getattr(faiss, "get_num_gpus", lambda: 0)()
                if num_gpus > 0:
                    res = faiss.StandardGpuResources()
                    self.index = faiss.index_cpu_to_gpu(res, 0, self.index)
                    print("✓ Índice migrado para GPU")
                else:
                    print("Aviso: USE_FAISS_GPU=1 definido mas sem GPU FAISS.")
        except Exception as e:
            print(f"Aviso: Falha ao migrar índice para GPU: {e}")

    def find_similar(self, query: str, top_k: int = 5) -> List[Tuple[Dict, float]]:
        """
        Encontra versos similares a uma query.

        Args:
            query: Texto da consulta
            top_k: Número de resultados a retornar

        Returns:
            Lista de tuplas (verso, score)
        """
        if self.index is None:
            raise ValueError("Índice não construído. Execute build_index primeiro.")

        # Gera embedding da query
        query_embedding = self.model.encode(
            [query], convert_to_numpy=True, normalize_embeddings=True
        )

        # Busca no índice
        scores, indices = self.index.search(query_embedding.astype("float32"), top_k)

        # Retorna versos com scores
        results = []
        for idx, score in zip(indices[0], scores[0]):
            if idx < len(self.verses):
                results.append((self.verses[idx], float(score)))

        return results

    def find_intertextual_links(
        self,
        verse_idx: int,
        top_k: int = 10,
        exclude_same_book: bool = False,
    ) -> List[Tuple[Dict, float]]:
        """
        Encontra links intertextuais para um verso específico.

        Args:
            verse_idx: Índice do verso no corpus
            top_k: Número de links a buscar
            exclude_same_book: Se True, exclui versos do mesmo livro

        Returns:
            Lista de tuplas (verso, score) ordenada por similaridade
        """
        if verse_idx >= len(self.verses):
            return []

        source_verse = self.verses[verse_idx]
        results = self.find_similar(source_verse["text"], top_k + 1)

        # Remove o próprio verso
        results = [r for r in results if r[0] != source_verse]

        # Filtra mesmo livro se solicitado
        if exclude_same_book:
            results = [r for r in results if r[0]["book"] != source_verse["book"]]

        return results[:top_k]

    def save_index(
        self,
        index_path: str = "indexes/faiss_nt.index",
        meta_path: str = "indexes/verses_meta.json",
    ):
        """Salva índice FAISS e metadados dos versos."""
        os.makedirs(os.path.dirname(index_path), exist_ok=True)

        if self.index is not None:
            faiss.write_index(self.index, index_path)
            print(f"✓ Índice salvo em {index_path}")

        if self.verses:
            with open(meta_path, "w", encoding="utf-8") as f:
                json.dump(self.verses, f, ensure_ascii=False, indent=2)
            print(f"✓ Metadados salvos em {meta_path}")

    def load_index(
        self,
        index_path: str = "indexes/faiss_nt.index",
        meta_path: str = "indexes/verses_meta.json",
    ):
        """Carrega índice FAISS e metadados dos versos."""
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print(
                f"✓ Índice carregado de {index_path} (" f"{self.index.ntotal} versos)"
            )

        if os.path.exists(meta_path):
            with open(meta_path, "r", encoding="utf-8") as f:
                self.verses = json.load(f)
            print(f"✓ Metadados carregados de {meta_path}")


if __name__ == "__main__":
    # Teste rápido
    from corpus_processor import CorpusProcessor

    # Carrega ou processa corpus
    processor = CorpusProcessor()
    verses = processor.load_corpus()

    if not verses:
        print("Processando corpus pela primeira vez...")
        verses = processor.process_all_sblgnt()
        processor.save_corpus(verses)

    if verses:
        # Cria engine e índice
        engine = IntertextualityEngine()
        engine.create_embeddings(verses)
        engine.build_index()
        engine.save_index()

        # Teste de busca
        print("\n--- Teste: buscar 'amor de Deus' ---")
        results = engine.find_similar("ἀγάπη θεοῦ", top_k=3)
        for verse, score in results:
            ref = f"{verse['book']} {verse['chapter']}:{verse['verse']}"
            print(f"{ref} (score: {score:.3f})")
            print(f"  {verse['text'][:80]}...")
