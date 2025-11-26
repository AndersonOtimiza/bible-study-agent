"""
Script para verificar disponibilidade e status de GPU/CUDA
"""

import sys


def check_gpu():
    print("=" * 60)
    print("🔍 Verificação de GPU/CUDA")
    print("=" * 60)

    # Verificar PyTorch
    try:
        import torch

        print(f"\n✅ PyTorch instalado: {torch.__version__}")

        if torch.cuda.is_available():
            print(f"✅ CUDA disponível: {torch.version.cuda}")
            print(f"✅ GPUs detectadas: {torch.cuda.device_count()}")

            for i in range(torch.cuda.device_count()):
                props = torch.cuda.get_device_properties(i)
                print(f"\n   GPU {i}: {props.name}")
                print(f"   • Compute Capability: {props.major}.{props.minor}")
                print(f"   • Memória Total: {props.total_memory / 1024**3:.2f} GB")
                print(f"   • Multiprocessadores: {props.multi_processor_count}")

                if torch.cuda.is_available():
                    mem_allocated = torch.cuda.memory_allocated(i) / 1024**3
                    mem_reserved = torch.cuda.memory_reserved(i) / 1024**3
                    print(f"   • Memória Alocada: {mem_allocated:.2f} GB")
                    print(f"   • Memória Reservada: {mem_reserved:.2f} GB")
        else:
            print("❌ CUDA não disponível")
            print("\n💡 Para habilitar GPU:")
            print(
                "   1. Instale NVIDIA CUDA Toolkit (https://developer.nvidia.com/cuda-downloads)"
            )
            print("   2. Instale PyTorch com CUDA:")
            print(
                "      pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu124"
            )

    except ImportError:
        print("❌ PyTorch não instalado")
        print("   pip install torch")

    # Verificar FAISS
    print("\n" + "=" * 60)
    try:
        import faiss

        print(
            f"✅ FAISS instalado: {faiss.__version__ if hasattr(faiss, '__version__') else 'versão desconhecida'}"
        )

        if hasattr(faiss, "get_num_gpus"):
            num_gpus = faiss.get_num_gpus()
            print(f"✅ FAISS detectou {num_gpus} GPU(s)")

            if num_gpus == 0:
                print("\n💡 Para usar FAISS com GPU:")
                print("   conda install -c pytorch faiss-gpu")
                print("   OU compile FAISS com suporte a GPU")
        else:
            print("⚠️  FAISS instalado sem suporte a GPU (faiss-cpu)")
            print("   Para GPU: conda install -c pytorch faiss-gpu")

    except ImportError:
        print("❌ FAISS não instalado")

    # Verificar Sentence Transformers
    print("\n" + "=" * 60)
    try:
        from sentence_transformers import SentenceTransformer

        print("✅ Sentence Transformers instalado")

        if torch.cuda.is_available():
            print("✅ Modelos de embedding usarão GPU automaticamente")
        else:
            print("⚠️  Modelos de embedding usarão CPU")

    except ImportError:
        print("❌ Sentence Transformers não instalado")

    print("\n" + "=" * 60)
    print("🎯 Recomendações:")
    print("=" * 60)

    if torch.cuda.is_available():
        print("✅ Seu sistema está configurado para usar GPU!")
        print("\nPara ativar no aplicativo:")
        print("   1. Adicione no .env: USE_FAISS_GPU=1")
        print("   2. Reinicie o servidor")
    else:
        print("⚠️  Configure CUDA para melhor performance:")
        print("   1. Verifique se sua GPU é NVIDIA (AMD não suportado por CUDA)")
        print("   2. Instale NVIDIA Driver atualizado")
        print("   3. Instale CUDA Toolkit")
        print("   4. Reinstale PyTorch com suporte a CUDA")

    print("=" * 60)


if __name__ == "__main__":
    check_gpu()
