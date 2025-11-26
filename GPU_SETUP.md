# Guia de Configuração GPU/CUDA

Este guia explica como habilitar e configurar o uso de GPU para acelerar o processamento no Bible Study Agent.

## 🎯 Requisitos

- **GPU NVIDIA** com suporte a CUDA (GTX/RTX 10xx ou superior)
- **CUDA Toolkit** instalado (versão 11.8 ou 12.x)
- **NVIDIA Driver** atualizado
- **Windows/Linux** com Python 3.10+

## 📦 Instalação

### 1. Verificar GPU Disponível

Execute o script de verificação:

```bash
python scripts/check_gpu.py
```

Este script mostrará:
- ✅ Status do PyTorch e CUDA
- ✅ GPUs detectadas e suas especificações
- ✅ Memória disponível
- ✅ Status do FAISS
- 💡 Recomendações de configuração

### 2. Instalar PyTorch com CUDA

**Para CUDA 12.4:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
```

**Para CUDA 11.8:**
```bash
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
```

**Verificar versão CUDA instalada:**
```bash
nvcc --version
# ou
nvidia-smi
```

### 3. Instalar FAISS-GPU (Opcional, mas recomendado)

FAISS-GPU acelera drasticamente a busca de similaridade.

**Via Conda (recomendado):**
```bash
conda install -c pytorch faiss-gpu
```

**Via pip (experimental):**
```bash
pip install faiss-gpu
```

## ⚙️ Configuração

### Arquivo `.env`

Copie o arquivo de exemplo:
```bash
copy .env.example .env
```

Configure as seguintes variáveis:

```env
# Habilitar FAISS em GPU
USE_FAISS_GPU=1

# Controle do device PyTorch
TORCH_DEVICE=auto  # ou 'cuda' para forçar GPU

# Opcional: limitar memória GPU para FAISS (em GB)
# FAISS_GPU_MEMORY_LIMIT=4
```

## 🚀 Uso

### Iniciar o Servidor

Com GPU configurada, basta iniciar normalmente:

```bash
python src/app.py
```

Ou com uvicorn:

```bash
uvicorn src.app:app --host 0.0.0.0 --port 8000 --reload
```

### Verificar Status

Ao iniciar, você verá logs indicando uso de GPU:

```
Carregando modelo paraphrase-multilingual-mpnet-base-v2...
✓ Modelo carregado na GPU: NVIDIA GeForce RTX 3080
  • Memória GPU: 10.00 GB
  • CUDA Version: 12.4
```

## 🔍 Monitoramento

### Monitorar Uso de GPU

**Windows:**
```powershell
nvidia-smi -l 1
```

**Linux:**
```bash
watch -n 1 nvidia-smi
```

### Verificar Memória GPU em Python

```python
import torch

if torch.cuda.is_available():
    print(f"GPU: {torch.cuda.get_device_name(0)}")
    print(f"Memória Alocada: {torch.cuda.memory_allocated(0)/1024**3:.2f} GB")
    print(f"Memória Reservada: {torch.cuda.memory_reserved(0)/1024**3:.2f} GB")
```

## 📊 Performance Esperada

### Sem GPU (CPU)
- **Embedding**: ~100 versos/segundo
- **Busca FAISS**: ~50ms por query (7.927 versos)

### Com GPU
- **Embedding**: ~500-1000 versos/segundo (5-10x mais rápido)
- **Busca FAISS**: ~5-10ms por query (5-10x mais rápido)
- **LLM Inference**: Depende do modelo e quantização

## 🐛 Troubleshooting

### "CUDA out of memory"

**Solução 1:** Limpar cache
```python
import torch
torch.cuda.empty_cache()
```

**Solução 2:** Reduzir batch size no `.env`
```env
FAISS_GPU_MEMORY_LIMIT=4
```

**Solução 3:** Usar CPU para FAISS
```env
USE_FAISS_GPU=0
```

### "CUDA not available"

1. Verificar se CUDA está instalado:
   ```bash
   nvcc --version
   ```

2. Verificar driver NVIDIA:
   ```bash
   nvidia-smi
   ```

3. Reinstalar PyTorch com CUDA:
   ```bash
   pip uninstall torch torchvision torchaudio
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

### FAISS não detecta GPU

FAISS-GPU requer instalação via conda:
```bash
conda install -c pytorch faiss-gpu
```

Ou compile manualmente com suporte a CUDA.

## 🎛️ Configurações Avançadas

### Múltiplas GPUs

Para usar GPU específica:

```python
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '0'  # Usar apenas GPU 0
```

Ou no `.env`:
```env
CUDA_VISIBLE_DEVICES=0,1  # Usar GPUs 0 e 1
```

### Mixed Precision (FP16)

Para reduzir uso de memória:

```env
TORCH_DTYPE=float16
```

(Requer modificação no código para suportar)

## 📚 Links Úteis

- [NVIDIA CUDA Toolkit](https://developer.nvidia.com/cuda-downloads)
- [PyTorch Installation](https://pytorch.org/get-started/locally/)
- [FAISS GPU Guide](https://github.com/facebookresearch/faiss/wiki/Faiss-on-the-GPU)
- [Sentence Transformers GPU](https://www.sbert.net/docs/usage/semantic_textual_similarity.html)

## ✅ Checklist Rápido

- [ ] GPU NVIDIA instalada e funcionando
- [ ] CUDA Toolkit instalado (nvcc --version)
- [ ] Driver NVIDIA atualizado (nvidia-smi)
- [ ] PyTorch com CUDA instalado
- [ ] FAISS-GPU instalado (opcional)
- [ ] `.env` configurado com USE_FAISS_GPU=1
- [ ] Script `check_gpu.py` executado com sucesso
- [ ] Servidor iniciado e logs mostram GPU ativa

---

**🎉 Pronto!** Seu sistema agora usa GPU para máxima performance.
