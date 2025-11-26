# AN Agent - Bible Study One Web

Agente de IA para estudos bíblicos profundos com **detecção de intertextualidade** usando NLP, embeddings semânticos e múltiplos modelos de linguagem (OpenAI, Anthropic, Cohere, Hugging Face).

## ✨ Funcionalidades

- 🔍 **Busca Semântica**: Encontre versos similares usando embeddings avançados
- 🔗 **Detecção de Intertextualidade**: Descubra conexões entre passagens bíblicas
- 🤖 **Múltiplos LLMs**: Suporte para OpenAI, Anthropic (Claude), Cohere e Hugging Face
- 📚 **Corpus Original**: Análise em grego (SBLGNT) e hebraico (planejado)
- ⚡ **FAISS**: Busca ultra-rápida com indexação vetorial
- 🌐 **API REST**: Endpoints FastAPI prontos para integração

## 📁 Estrutura do Projeto

```
├── src/
│   ├── app.py                          # FastAPI application
│   ├── services/
│   │   ├── bible_service.py            # Serviço principal com LLMs
│   │   ├── corpus_processor.py         # Processamento de textos bíblicos
│   │   └── intertextuality_engine.py   # Motor de busca semântica
│   └── static/
│       └── index.html                  # Interface web
├── scripts/
│   └── setup_corpus.py                 # Script de setup inicial
├── data/                               # Corpus processado (gerado)
├── models/                             # Modelos baixados (gerado)
├── indexes/                            # Índices FAISS (gerado)
├── Documentação/Bible/
│   └── sblgnt/                         # Arquivos MorphGNT (NT grego)
├── requirements.txt
└── .env                                # Variáveis de ambiente (criar)
```

## 🚀 Início Rápido

### 1. Configurar Ambiente

```bash
# Criar ambiente virtual
python -m venv .venv

# Ativar ambiente
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configurar Variáveis de Ambiente

Crie um arquivo `.env` na raiz do projeto:

```bash
# === Provedor de LLM ===
# Opções: OPENAI, ANTHROPIC, COHERE, HF
LLM_PROVIDER=OPENAI

# === Chaves de API (configure apenas o provider escolhido) ===
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
COHERE_API_KEY=...
HF_API_TOKEN=hf_...

# === Hugging Face (se LLM_PROVIDER=HF) ===
HF_MODEL=gpt2  # ou outro modelo disponível
```

### 3. Processar Corpus e Construir Índices

**IMPORTANTE**: Execute este comando antes da primeira utilização:

```bash
python scripts/setup_corpus.py
```

Este script irá:
- Processar textos SBLGNT (NT grego) para JSON
- Gerar embeddings com Sentence Transformers
- Construir índice FAISS para busca rápida
- Testar a busca semântica

⏱️ **Tempo estimado**: 5-10 minutos (depende do hardware)

### 4. Iniciar Aplicação

```bash
python src/app.py
```

Acesse: `http://localhost:8000`

## 📡 Endpoints da API

### POST `/ask`
Pergunta sobre estudos bíblicos usando o LLM configurado.

```json
{
  "question": "Qual o significado de ἀγάπη no Novo Testamento?"
}
```

### POST `/find-similar`
Busca versos similares semanticamente.

```json
{
  "query": "ἀγάπη θεοῦ",
  "top_k": 5
}
```

**Resposta:**
```json
{
  "query": "ἀγάπη θεοῦ",
  "results": [
    {
      "book": "John",
      "chapter": 3,
      "verse": 16,
      "text": "Οὕτως γὰρ ἠγάπησεν ὁ θεὸς τὸν κόσμον...",
      "similarity_score": 0.87
    }
  ]
}
```

### POST `/explain-links`
Encontra links intertextuais e explica conexões usando LLM.

```json
{
  "query": "Ἐν ἀρχῇ ἦν ὁ λόγος",
  "top_k": 5
}
```

## 🔧 Configuração de Provedores

### OpenAI (Padrão)
```bash
LLM_PROVIDER=OPENAI
OPENAI_API_KEY=sk-...
```
Modelos: `gpt-4o-mini`, `gpt-4o`, `gpt-4-turbo`

### Anthropic (Claude)
```bash
LLM_PROVIDER=ANTHROPIC
ANTHROPIC_API_KEY=sk-ant-...
```
Modelos: `claude-2.1`, `claude-3-opus`, `claude-3-sonnet`

### Cohere
```bash
LLM_PROVIDER=COHERE
COHERE_API_KEY=...
```
Modelos: `command`, `command-xlarge-nightly`

### Hugging Face
```bash
LLM_PROVIDER=HF
HF_API_TOKEN=hf_...
HF_MODEL=meta-llama/Llama-2-7b-chat-hf
```

## 🧪 Testando

```bash
# Testar processamento de corpus
python src/services/corpus_processor.py

# Testar motor de intertextualidade
python src/services/intertextuality_engine.py

# Testar API (com servidor rodando)
curl -X POST http://localhost:8000/find-similar \
  -H "Content-Type: application/json" \
  -d '{"query": "ἀγάπη", "top_k": 3}'
```

### Testes automatizados (pytest)

```bash
pytest -q
```

Se estiver sem o índice FAISS, alguns testes retornam listas vazias por design.

## 📚 Dependências Principais

- **FastAPI**: Framework web assíncrono
- **Sentence Transformers**: Geração de embeddings multilíngues
- **FAISS**: Busca vetorial eficiente (Facebook AI)
- **OpenAI/Anthropic/Cohere SDKs**: Integração com LLMs
- **PyTorch**: Backend para modelos de ML

## 🗺️ Roadmap

- [x] Suporte a múltiplos LLMs
- [x] Busca semântica com FAISS
- [x] Processamento de SBLGNT (NT grego)
- [ ] Processamento de BHS (AT hebraico)
- [ ] Integração com textPAIR para validação de paralelos
- [ ] Integração com SimAlign para alinhamento palavra-a-palavra
- [ ] Interface web interativa melhorada
- [ ] Exportação de grafos de intertextualidade
- [ ] Cache de embeddings
- [ ] Suporte a Docker

## 🖥️ Suporte a GPU (CUDA) e Ollama

### GPU (PyTorch + FAISS)
Para usar aceleração NVIDIA:
1. Instale drivers NVIDIA e verifique com `nvidia-smi`.
2. Instale PyTorch com CUDA (exemplo CUDA 12.4):
  ```bash
  pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
  ```
3. Substitua `faiss-cpu` por `faiss-gpu` (preferencial via Conda/WSL):
  ```bash
  conda install -c pytorch faiss-gpu
  ```
4. Defina no `.env` (opcional) para migrar o índice FAISS para GPU:
  ```bash
  USE_FAISS_GPU=1
  ```
5. Rode novamente o pipeline de corpus se quiser regenerar embeddings.

O código detecta automaticamente `cuda` via `torch.cuda.is_available()` e move o modelo de embeddings para GPU. Se `USE_FAISS_GPU=1` e FAISS GPU estiver disponível, o índice também é migrado.

### Ollama (Modelos Locais)
Permite usar modelos locais (ex.: `llama3`, `mistral`, etc.) sem custo por token.

1. Instale Ollama:
  - Windows / WSL:
    ```bash
    curl -fsSL https://ollama.com/install.sh | bash
    ```
  - Ou instalador gráfico (se disponível).
2. Baixe um modelo:
  ```bash
  ollama pull llama3
  ```
3. Ajuste `.env`:
  ```bash
  LLM_PROVIDER=OLLAMA
  OLLAMA_HOST=http://localhost:11434
  OLLAMA_MODEL=llama3
  ```
4. Inicie a API normal (`python src/app.py`).

O provider OLLAMA utiliza o endpoint local `POST /api/generate` para gerar respostas. Para trocar de modelo basta alterar `OLLAMA_MODEL` e reiniciar.

### Dicas de Performance
- Prefira modelos menores para prototipagem (7B / 8B).
- Regere embeddings apenas quando alterar o modelo de Sentence Transformers.
- Mantenha `normalize_embeddings=True` para melhor consistência na similaridade coseno.
- Use GPU apenas se o tamanho do corpus justificar (reduz latência em consultas grandes).

## 📄 Licença

MIT

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor, abra uma issue ou PR.

## 🧱 Arquitetura de Providers LLM

Os provedores LLM foram desacoplados via interface em `src/providers/`:
- `llm_base.py` (interface `LLMProvider` + `DummyProvider`)
- `openai_provider.py`, `anthropic_provider.py`, `cohere_provider.py`, `hf_provider.py`, `ollama_provider.py`

O serviço principal (`src/services/bible_service.py`) injeta o provider conforme `LLM_PROVIDER`.

## 🐳 Docker

Um `Dockerfile` foi adicionado para facilitar a execução em container:

```bash
# Build
docker build -t an-agent-biblestudy .

# Run (porta 8000)
docker run -p 8000:8000 an-agent-biblestudy
```

Notas:
- O container não gera o índice por padrão. Para construir dentro do container, execute `python scripts/setup_corpus.py` interativamente.
- Monte volumes para `data/` e `indexes/` caso queira persistência fora do container.
