"""
Script para controlar GPU em runtime via API
"""

import sys

import requests


def get_status():
    """Obtém status atual da GPU."""
    try:
        response = requests.get("http://localhost:8000/gpu/status")
        data = response.json()

        print("=" * 60)
        print("🔍 Status GPU/CUDA")
        print("=" * 60)
        print(f"Device Atual: {data['device'].upper()}")
        print(f"CUDA Disponível: {'✅ Sim' if data['cuda_available'] else '❌ Não'}")

        if data["cuda_available"]:
            print(f"\nGPU: {data['gpu_name']}")
            print(f"Memória Total: {data['gpu_memory_total']:.2f} GB")
            print(f"Memória Alocada: {data['gpu_memory_allocated']:.2f} GB")
            print(f"Memória Reservada: {data['gpu_memory_reserved']:.2f} GB")
            print(f"CUDA Version: {data['cuda_version']}")

        print("=" * 60)
        return data

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando em http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def set_device(device: str):
    """Altera o device (cpu/cuda)."""
    try:
        response = requests.post(
            "http://localhost:8000/gpu/set", params={"device": device}
        )
        data = response.json()

        if data["status"] == "success":
            print(f"✅ {data['message']}")
        else:
            print(f"❌ {data['message']}")

        return data

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando em http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def toggle():
    """Alterna entre CPU e GPU."""
    try:
        response = requests.post("http://localhost:8000/gpu/toggle")
        data = response.json()

        if data["status"] == "success":
            print(f"✅ {data['message']}")
        else:
            print(f"❌ {data['message']}")

        return data

    except requests.exceptions.ConnectionError:
        print("❌ Erro: Servidor não está rodando em http://localhost:8000")
        return None
    except Exception as e:
        print(f"❌ Erro: {e}")
        return None


def show_help():
    """Mostra ajuda."""
    print(
        """
🎮 Controle de GPU - Bible Study Agent

Uso:
    python scripts/gpu_control.py [comando]

Comandos:
    status      Mostra status atual da GPU
    cpu         Muda para CPU
    cuda        Muda para GPU (CUDA)
    toggle      Alterna entre CPU e GPU
    help        Mostra esta ajuda

Exemplos:
    python scripts/gpu_control.py status
    python scripts/gpu_control.py cuda
    python scripts/gpu_control.py toggle
"""
    )


def main():
    if len(sys.argv) < 2:
        show_help()
        return

    command = sys.argv[1].lower()

    if command == "status":
        get_status()
    elif command == "cpu":
        set_device("cpu")
    elif command == "cuda":
        set_device("cuda")
    elif command == "toggle":
        toggle()
    elif command == "help":
        show_help()
    else:
        print(f"❌ Comando desconhecido: {command}")
        show_help()


if __name__ == "__main__":
    main()
