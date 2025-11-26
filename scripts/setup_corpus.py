#!/usr/bin/env python3
"""
Script de setup para processar corpus bíblico e construir índices FAISS.
Execute este script antes de iniciar a aplicação pela primeira vez.
"""

import os
import sys

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.services.corpus_processor import CorpusProcessor
from src.services.intertextuality_engine import IntertextualityEngine


def main():
    print("=" * 60)
    print("SETUP: Processamento de Corpus e Construção de Índices")
    print("=" * 60)
    
    # Passo 1: Processar corpus SBLGNT
    print("\n[1/3] Processando corpus do Novo Testamento (SBLGNT)...")
    processor = CorpusProcessor()
    
    # Verifica se já existe
    corpus_file = "data/nt_corpus.json"
    if os.path.exists(corpus_file):
        print(f"✓ Corpus já existe em {corpus_file}")
        verses = processor.load_corpus(corpus_file)
    else:
        verses = processor.process_all_sblgnt()
        if not verses:
            print("✗ ERRO: Nenhum verso encontrado. Verifique se os arquivos SBLGNT estão em:")
            print("  Documentação/Bible/sblgnt/")
            return 1
        processor.save_corpus(verses, corpus_file)
    
    print(f"✓ {len(verses)} versos processados")
    
    # Passo 2: Criar embeddings
    print("\n[2/3] Criando embeddings (pode levar alguns minutos)...")
    print("⏳ Baixando modelo Sentence Transformers (primeira vez pode demorar)...")
    engine = IntertextualityEngine()
    
    # Verifica se índice já existe
    index_file = "indexes/faiss_nt.index"
    if os.path.exists(index_file):
        print(f"✓ Índice já existe em {index_file}")
        response = input("Reconstruir índice? (s/N): ").strip().lower()
        if response != 's':
            print("Usando índice existente.")
            return 0
    
    print("⏳ Gerando embeddings vetoriais (progresso abaixo)...")
    embeddings = engine.create_embeddings(verses)
    print(f"✓ Embeddings criados: {embeddings.shape}")
    
    # Passo 3: Construir índice FAISS
    print("\n[3/3] Construindo índice FAISS...")
    print("⏳ Indexando versos para busca rápida...")
    engine.build_index(embeddings)
    engine.save_index()
    
    # Teste rápido
    print("\n" + "=" * 60)
    print("TESTE: Buscando versos similares a 'ἀγάπη' (amor)")
    print("=" * 60)
    print("⏳ Executando busca semântica...")
    
    results = engine.find_similar("ἀγάπη", top_k=3)
    for i, (verse, score) in enumerate(results, 1):
        ref = f"{verse['book']} {verse['chapter']}:{verse['verse']}"
        print(f"\n{i}. {ref} (score: {score:.3f})")
        print(f"   {verse['text'][:80]}...")
    
    print("\n" + "=" * 60)
    print("✓ SETUP CONCLUÍDO COM SUCESSO!")
    print("=" * 60)
    print("\nVocê pode agora iniciar a aplicação com:")
    print("  python src/app.py")
    print("\nOu testar os endpoints:")
    print("  POST /find-similar")
    print("  POST /explain-links")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
