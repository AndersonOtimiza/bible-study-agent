# 🎮 Controle de GPU em Runtime

Este projeto permite **ligar e desligar a GPU** dinamicamente sem reiniciar o servidor.

## 🚀 Como Funcionar

### 1. Via Interface Web

**Botão de Status GPU** (ao lado do seletor de modelo):

- **🖥️ CPU** - Indica que está rodando em CPU
- **🚀 GPU** - Indica que está rodando em GPU

**Para alternar:**
- Clique no botão de status
- O sistema muda automaticamente entre CPU e GPU
- Uma mensagem de confirmação aparece no chat

**Status em Tempo Real:**
- Hover sobre o botão mostra informações da GPU
- Atualização automática a cada 10 segundos

### 2. Via Script Python

```bash
# Ver status atual
python scripts/gpu_control.py status

# Mudar para GPU
python scripts/gpu_control.py cuda

# Mudar para CPU
python scripts/gpu_control.py cpu

# Alternar automaticamente
python scripts/gpu_control.py toggle
```

**Exemplo de saída:**
```
============================================================
🔍 Status GPU/CUDA
============================================================
Device Atual: CUDA
CUDA Disponível: ✅ Sim

GPU: NVIDIA GeForce RTX 3080
Memória Total: 10.00 GB
Memória Alocada: 0.45 GB
Memória Reservada: 0.50 GB
CUDA Version: 12.4
============================================================
```

### 3. Via API REST

**GET /gpu/status** - Obter status atual
```bash
curl http://localhost:8000/gpu/status
```

Resposta:
```json
{
  "device": "cuda",
  "cuda_available": true,
  "gpu_name": "NVIDIA GeForce RTX 3080",
  "gpu_memory_total": 10.0,
  "gpu_memory_allocated": 0.45,
  "gpu_memory_reserved": 0.50,
  "cuda_version": "12.4"
}
```

**POST /gpu/set?device=cuda** - Mudar para GPU
```bash
curl -X POST "http://localhost:8000/gpu/set?device=cuda"
```

**POST /gpu/set?device=cpu** - Mudar para CPU
```bash
curl -X POST "http://localhost:8000/gpu/set?device=cpu"
```

**POST /gpu/toggle** - Alternar automaticamente
```bash
curl -X POST http://localhost:8000/gpu/toggle
```

Resposta:
```json
{
  "status": "success",
  "message": "Device alterado de cpu para cuda",
  "old_device": "cpu",
  "new_device": "cuda"
}
```

## ⚙️ Configuração

### Variáveis de Ambiente (.env)

```env
# Controle de GPU
USE_GPU=1              # 1 = habilitado, 0 = desabilitado
TORCH_DEVICE=auto      # auto, cpu ou cuda

# FAISS GPU (opcional)
USE_FAISS_GPU=1        # 1 = usa GPU para índice FAISS
```

### Requisitos

Para usar GPU, você precisa:

1. ✅ **GPU NVIDIA** compatível com CUDA
2. ✅ **CUDA Toolkit** instalado (11.8+ ou 12.x)
3. ✅ **PyTorch com CUDA** instalado:
   ```bash
   pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124
   ```

Verificar instalação:
```bash
python scripts/check_gpu.py
```

## 📊 Quando Usar Cada Modo

### 🖥️ CPU Mode
**Use quando:**
- Quer economizar energia
- GPU está sendo usada por outro processo
- Testando compatibilidade
- Rodando em máquina sem GPU

**Performance:**
- Embeddings: ~100 versos/segundo
- Busca FAISS: ~50ms por query

### 🚀 GPU Mode
**Use quando:**
- Quer máxima performance
- Processando grandes volumes de texto
- GPU disponível e ociosa
- Produção com alta demanda

**Performance:**
- Embeddings: ~500-1000 versos/segundo (5-10x mais rápido)
- Busca FAISS: ~5-10ms por query (5-10x mais rápido)

## 🔄 Comportamento

### O que acontece ao alternar:

1. **Modelo de Embeddings** é recarregado no novo device
2. **Índice FAISS** permanece em memória (não é recarregado)
3. **Conexão permanece ativa** (sem reinício do servidor)
4. **Cache é mantido** (não é limpo)

### Memória

**CPU → GPU:**
- Consome memória GPU adicional
- Se falhar por falta de memória, reverte para CPU

**GPU → CPU:**
- Libera memória GPU automaticamente
- Sempre funciona

## 🐛 Troubleshooting

### "CUDA not available"

GPU não está configurada. Execute:
```bash
python scripts/check_gpu.py
```

E siga as instruções.

### "CUDA out of memory"

**Solução 1:** Limpar cache GPU
```python
import torch
torch.cuda.empty_cache()
```

**Solução 2:** Fechar outros programas usando GPU

**Solução 3:** Usar CPU mode:
```bash
python scripts/gpu_control.py cpu
```

### Alternância não funciona

Verifique logs do servidor:
```bash
# Terminal onde o servidor está rodando mostrará:
# ✓ Modelo carregado na GPU: NVIDIA GeForce RTX 3080
# ou
# ✓ Modelo carregado em CPU
```

## 📝 Logs

O servidor mostra informações detalhadas ao alternar:

```
Carregando modelo paraphrase-multilingual-mpnet-base-v2...
✓ Modelo carregado na GPU: NVIDIA GeForce RTX 3080
  • Memória GPU: 10.00 GB
  • CUDA Version: 12.4
```

## 🎯 Dicas

1. **Mantenha GPU habilitada** em produção para melhor performance
2. **Use CPU** durante desenvolvimento se GPU estiver ocupada
3. **Monitore uso de memória** com `nvidia-smi -l 1`
4. **Alterne via web UI** para conveniência
5. **Use script** para automação/testes

## 📚 Links Relacionados

- [GPU_SETUP.md](./GPU_SETUP.md) - Guia completo de instalação
- [scripts/check_gpu.py](./scripts/check_gpu.py) - Verificação de GPU
- [scripts/gpu_control.py](./scripts/gpu_control.py) - Controle via terminal

---

**✨ Agora você tem controle total sobre CPU/GPU em tempo real!**
