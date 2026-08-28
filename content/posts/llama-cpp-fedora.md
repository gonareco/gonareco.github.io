---
title: "Cómo compilé llama.cpp en Fedora con aceleración AMD Radeon"
date: 2026-05-12T10:00:00-03:00
draft: false
tags: ["LLM", "Fedora", "AMD", "ROCm", "GPU"]
---

## Por qué compilar manualmente y no usar Ollama

Cuando quise correr modelos locales en mi laptop, probé primero Ollama
con Podman. Funcionaba, pero noté dos problemas:

1.  **Overhead del contenedor:** Cada vez que corría un modelo, consumía
    \~500MB de RAM solo en el contenedor.
2.  **Detección automática de GPU:** Ollama no detectaba mi Radeon 630.

Decidí compilar llama.cpp directamente para tener **control total** y
aprovechar mi hardware al máximo.

## Mi hardware

- CPU: AMD Ryzen 5 7000 series
- GPU: AMD Radeon 630 (4GB)
- RAM: 32 GB
- OS: Fedora 44
- LLM Elegido: Qwen2.5-Coder:3b

## El problema: ROCm en Fedora no es tan simple

AMD tiene ROCm (Radeon Open Compute), el equivalente a CUDA de NVIDIA.
Pero oficialmente, ROCm solo soporta Ubuntu y RHEL. Fedora no está en la
lista oficial.

Sin embargo, los paquetes existen en los repositorios de Fedora. La
documentación es escasa, pero funciona.

## Dependencias necesarias

    bash
    sudo dnf install rocm-hip-libraries rocm-device-libs
    rocm-clinfo
    sudo dnf install gcc-c++ make cmake

### rocm-hip-libraries es la clave. Proporciona las bibliotecas HIP que usa llama.cpp para hablar con la GPU.

### Compilación bash

    bash
    git clone https://github.com/ggerganov/llama.cpp
    cd llama.cpp
    make
    LLAMA_HIPBLAS=1

LLAMA_HIPBLAS=1 le dice al Makefile que compile con soporte para AMD
GPU. Sin esta flag, compila solo para CPU. Este fue el primer problema que encontré al correr correr por primera vez, la diferencia entre aprovechar la GPU o solo el procesador es ABISMAL.
En principio el llm no usaba la GPU.

Dos soluciones:

### Agregar mi usuario al grupo render:

    bash
    sudo usermod -a -G render \$USER

### Forzar la versión de GFX para mi Radeon 630 (que es gfx902):

    bash
    export HSA_OVERRIDE_GFX_VERSION=10.3.0

Lo agregué a mi .bashrc para no tener que escribirlo cada vez.

### Comprobación bash

    bash
    ./main --help \| grep -i hip \#
    
Si ves información sobre HIP, está bien, se está usando la GPU (igual te vas a dar cuenta porque te tira respuestas mucho más rápidas que sólo corriendo en el procesador)

    bash
    rocm-smi \# Muestra temperatura, uso de memoria, etc.
    
>Rendimiento real
>
> (t/s) GPU (t/s) TinyLlama 1.1B \~15 \~60 Llama 2 7B \~4 \~25


Probé dos modelos en GGUF (formato cuantizado): Modelo Parámetros CPU

La aceleración por GPU multiplica por 4 la velocidad. La diferencia es
abismal. ¿Para qué hacer esto? Bueno, como muchas cosas para probar, optimizar, aprender, jugar y aprovechar los (escasos o no) recursos.


### ROCm en Fedora sí funciona, aunque AMD no lo promocione.

Compilar manualmente da control **total**: podés elegir qué flags activar.

>HSA_OVERRIDE_GFX_VERSION es clave para GPUs Radeon más viejas o no oficialmente soportadas.
>
>El overhead de los contenedores (Ollama, Docker, Podman) no es despreciable cuando tenés recursos justos (como yo).

### Conclusión

Si tenés una GPU AMD y usás Fedora, vale la pena compilar llama.cpp. El proceso es simple una vez que
conocés las dependencias correctas.

El próximo paso podría ser conectar esto con una API estilo OpenAI para usarlo
desde otros programas o servicios. Llama.cpp ya viene con su interfaz web para usarla, guarda conversaciones y funciona de maravilla ;-).

[llama.cpp en GitHub](https://github.com/ggml-org/llama.cpp)

[ROCm instalación para Linux](https://rocm.docs.amd.com/projects/install-on-linux/en/latest/)
