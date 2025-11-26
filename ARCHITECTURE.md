# AN Agent - Bible Study One Web – Arquitetura Técnica

## 1. Visão Geral
O sistema é um agente de estudo bíblico com foco em **busca semântica** e **detecção de intertextualidade** sobre o corpus do Novo Testamento em grego (SBLGNT). A arquitetura segue um pipeline: Corpus bruto → Processamento → Embeddings → Índice Vetorial → API (consulta + explicação via LLM).

## 2. Componentes Principais
| Componente | Arquivo | Responsabilidade | Observações |
|------------|---------|------------------|-------------|
| API HTTP | `src/app.py` | Expor endpoints REST com FastAPI | Monta estáticos e injeta `BibleService` |
| Orquestrador | `src/services/bible_service.py` | Coordena LLM + busca semântica + explicações | Lazy loading de provedores e engine |
| Processador de Corpus | `src/services/corpus_processor.py` | Limpar, normalizar e estruturar versos | Gera `data/nt_corpus.json` e metadados |
| Motor Semântico | `src/services/intertextuality_engine.py` | Carregar embeddings + índice FAISS e executar similaridade | Trabalha com normalização coseno |
| Setup Automatizado | `scripts/setup_corpus.py` | Pipeline end‑to‑end inicial | Idempotente; recria índice se ausente |
| Dados Processados | `data/nt_corpus.json` | Versos estruturados (array de objetos) | Fonte para embedding e busca |
| Índice Vetorial | `indexes/faiss_nt.index` | Índice FAISS persistido | Carregado somente quando necessário |
| Metadados | `indexes/verses_meta.json` | Mapeamento verso → posição / referencia | Facilita reconstrução de contexto |

## 3. Fluxo de Dados
1. Corpus bruto (MorphGNT) lido em `scripts/setup_corpus.py`.
2. Normalização (remoção de sinais irrelevantes, padronização de whitespace).
3. Geração de embeddings usando `SentenceTransformers(paraphrase-multilingual-mpnet-base-v2)`.
4. Construção de índice FAISS (`IndexFlatIP` ou similar) → persistido.
5. API carrega `BibleService`, que por demanda carrega `IntertextualityEngine` (lazy) quando `/find-similar` ou `/explain-links` é chamado.
6. Para `/explain-links`: busca top-K → passa lista de versos ao LLM para gerar explicação consolidada.

## 4. Endpoints (Contrato Resumido)
| Endpoint | Método | Entrada | Saída | Observações |
|----------|--------|---------|-------|-------------|
| `/ask` | POST | `{question}` | `{response}` | Interação direta com LLM |
| `/find-similar` | POST | `{query, top_k}` | `{query, results[]}` | Similaridade semântica pura |
| `/explain-links` | POST | `{query, top_k}` | `{query, links[], explanation}` | Combina busca + geração LLM |
| `/health` | GET | - | `{status:"ok"}` | Verificação básica |

## 5. Estratégia de Similaridade
- Embeddings normalizados (vetores L2) → similaridade coseno via produto interno.
- FAISS escolhido pelo custo baixo de CPU e escalabilidade futura (GPU).
- `top_k` padrão = 5; pode ser elevado dependendo de casos de estudo (ex.: comparação literária ampla).

## 6. Gestão de Provedores LLM
| Provider | Variáveis | Observações |
|----------|-----------|-------------|
| OpenAI | `OPENAI_API_KEY` | Modelos GPT-4o / mini |
| Anthropic | `ANTHROPIC_API_KEY` | Modelos Claude 2/3 |
| Cohere | `COHERE_API_KEY` | `command` / variantes |
| Hugging Face | `HF_API_TOKEN`, `HF_MODEL` | Inference API (latência variável) |
| Ollama (planejado) | `OLLAMA_HOST`, `OLLAMA_MODEL` | Local; reduz custo e dependência externa |

Decisão: uso de variável única `LLM_PROVIDER` para reduzir branching complexo e facilitar troca operacional.

## 7. Lazy Loading / Performance
- `BibleService` só inicializa pesos e índice quando necessário (evita custo de cold start para rotas simples como `/health`).
- Recomendado adicionar caching de resultados frequentes → estratégia de dicionário in-memory ou Redis futuro.
- Possível migração FAISS → GPU se `USE_FAISS_GPU=1` e dependência instalada.

## 8. Tratamento de Erros (Sugestões de Evolução)
| Cenário | Ação Atual | Recomendação |
|---------|------------|--------------|
| Índice ausente | Retorno vazio ou exceção interna | Validar no startup e retornar mensagem clara |
| Provedor LLM inválido | Pode gerar KeyError | Validar `LLM_PROVIDER` e fallback documentado |
| Timeout LLM | Depende do SDK | Adicionar timeout + retry exponencial |
| 429 / Rate limit | Sem tratamento unificado | Implementar backoff por provider |
| Input vazio | Pode gerar embedding vazio | Sanitizar e retornar 400 |

## 9. Segurança Básica
- Chaves em `.env` (não commitadas).
- Faltam: limite de tokens por requisição, proteção contra prompt injection nas explicações, logging estruturado.
- Recomendado: adicionar middleware de validação + rate limiting (ex.: `slowapi`).

## 10. Testes
| Tipo | Arquivo(s) | Cobertura atual | Próximos passos |
|------|------------|-----------------|-----------------|
| API | `tests/test_api.py` | Básico (verificar endpoints) | Mock embeddings / LLM p/ previsibilidade |
| Engine | `tests/test_intertextuality_engine.py` | Similaridade fundamental | Adicionar caso de regressão para normalização |
| Serviço | (não presente) | - | Criar testes de `BibleService` com fixtures |

## 11. Roadmap Técnico Priorizado
1. (Alto) Cache de embeddings e resultados de queries mais frequentes.
2. (Alto) Testes unitários para `BibleService` + mocks de LLM.
3. (Alto) Dockerfile + compose para facilitar deploy.
4. (Médio) BHS (hebraico) → pipeline paralelo; particionar corpus para escalabilidade.
5. (Médio) Exportação de grafos de intertextualidade (NetworkX + JSON serializado).
6. (Médio) textPAIR + SimAlign para validação e alinhamento lexical.
7. (Baixo) Middleware de rate limiting + observabilidade (Prometheus / OpenTelemetry).
8. (Baixo) Interface web enriquecida (visualização interativa de paralelos).

## 12. Escalabilidade / Fatores
| Fator | Estratégia Atual | Próxima Etapa |
|-------|------------------|---------------|
| Crescimento de corpus | Único índice | Sharding por Testamento / língua |
| Concorrência de requisições | Single-process Uvicorn | Gunicorn + workers / async pooling |
| Latência LLM | Chamada direta | Introduzir camadas de streaming / fallback local |
| Custo | Dependência de APIs | Modelos locais + quantização |

## 13. Observabilidade (Sugestões)
- Adicionar logging estruturado (JSON) por requisição.
- Métricas: tempo de resposta por endpoint, hits de cache, tempo de busca FAISS, tokens LLM.
- Eventual tracing: OpenTelemetry + agente (Jaeger).

## 14. Extensibilidade
Pontos de extensão claros:
- Substituir modelo de embeddings → basta atualizar o script de setup e regenerar índice.
- Adicionar novos providers LLM → implementar adaptador padronizado em `BibleService`.
- Introduzir ranking híbrido (BM25 + vetor) → criar módulo `hybrid_ranker.py` mantendo interface `find_similar_verses`.

## 15. Sugestão de Próxima Refatoração
Criar camada de abstração:
```
interfaces/
  llm_provider.py  # Protocolo/base
providers/
  openai_provider.py
  anthropic_provider.py
  cohere_provider.py
  hf_provider.py
```
Facilita testes e substituição futura.

## 16. Riscos Atuais
| Risco | Impacto | Mitigação |
|-------|---------|-----------|
| Acoplamento direto LLM no serviço | Dificulta testes | Introduzir interface / DI |
| Ausência de caching | Latência / custo | Implementar LRU / Redis |
| Falta de validação sanitária | Possível entrada inválida | Pydantic + regras extras |
| Crescimento sem monitoramento | Degrada performance | Métricas + autoscaling futuramente |

## 17. Checklist de Evolução Inicial
- [ ] Adicionar testes para `BibleService`
- [ ] Criar interface de provider
- [ ] Incluir caching simples (in-memory)
- [ ] Adicionar validação de entrada (comprimento mínimo)
- [ ] Adicionar tratamento para índice inexistente

---
**Status Arquitetura:** MVP sólido, pronto para modularização e expansão.
