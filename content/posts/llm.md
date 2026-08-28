---
title: "LLMs locales con llama.cpp: por qué trabajo híbridamente (nube y local)"
date: 2026-06-12
tags: ["LLM", "llama.cpp", "Qwen", "Mistral", "GPU", "ROCm", "Linux"]
---

## El problema: depender de la nube para todo

No soy un experto en LLMs, pero descubrí algunas cuestiones que podrían mejorarse sin gastar un peso en el camino. Los LLMs online gratuitos funcionan, pero:
- Los datos sensibles (normalización de direcciones, encuestas de programas sociales, algunos proyectos personales de desarrollo) no pueden salir de mi máquina.
- Claude cuesta. ChatGPT también, si querés algo decente. Deepseek en su versión gratuita me es bastante funcional pero:
- Sin internet no anda.
- Los modelos online en su mayoría fueron entrenados en inglés, por lo que responden por defecto con las estructuras de antítesis enfática, esos ejemplos de (No es, es...), así como la excesiva explicación itemizada o ejemplificada típica de ese idioma. Los modelos inevitablemente arrastran ese *defecto* en nuestro lenguaje. Eso me molesta muchísimo.

Necesitaba algo que corriera localmente sin morir en el intento, con el objetivo de usarlo principalmente para desarrollo, revisión de código y esas cuestiones más bien técnicas.

> Nota
>
> Estoy probando y haciendo ajustes sobre modelos entrenados en español, específicamente Carballo y Cabra, dos LLMs que desconocía y parece que andarán muy bien. Después les cuento.

## La solución: Hibridar entre LLMs locales con llama.cpp y bueno, la nube.

Hablamos ya aquí de llama.cpp: una implementación en C++ de modelos como LLaMA, Qwen, Mistral. Liviana, eficiente, y lo mejor: **corre en CPU y GPU**. Podés ir al post haciendo [clic acá](https://gonareco.github.io/blog/posts/llama-cpp-fedora/)

## ¿Por qué no usé Ollama?

Ollama es cómodo (un comando y listo), pero (ya explicado en otro post pero lo explicito acá de nuevo)
- Overhead del contenedor (~500MB de RAM extra).
- No detectaba mi GPU Radeon 630 automáticamente.
- Quería tener control total sobre la compilación (flags, optimizaciones, integración con ROCm).

## Modelos que probé (y por qué me quedé con Qwen y Mistral - por ahora)

| Modelo | Parámetros | Uso | RAM necesaria | GPU (Radeon 630) |
|--------|-----------|-----|---------------|------------------|
| TinyLlama | 1.1B | Pruebas rápidas | ~2GB | Sí (rápido) |
| **Qwen2.5-Coder** | **3B** | **Código (R, Python, SQL)** | **~4GB** | **Sí, entero** |
| **Mistral** | **7B** | **General / Razonamiento** | **~8GB** | **Parcial (GPU + RAM)** |
| Llama 2 | 7B | General | ~8GB | Parcial |
| Mixtral | 8x7B | Avanzado | ~32GB | No (solo CPU, lento) |

Qwen se especializa en código (ideal para Data Scientist y desarrollo en general). Mistral es mejor para razonamiento general.
Por lo que pude evidenciar sin demasiado fine-tunning Mistral responde mejor a consultas generales del tipo "¿Qué es el ser?", mientras que Qwen es más preciso para optimizar código.


## Modelos que se pueden correr con GPU + RAM

Cuando un modelo no entra entero en la GPU (ej: Mistral 7B en mi Radeon de 4GB), llama.cpp permite dividirlo:

- Parte del modelo en GPU (ej: 20 capas)
- Resto en RAM (el resto de las capas)

La pérdida de rendimiento es mínima si la GPU es rápida, en mi caso no se siente prácticamente nada.

## Rendimiento en mi hardware (Ryzen 5 7535 + Radeon 630 + 32GB RAM)

| Modelo | Calidad | t/s (GPU) | t/s (CPU) | Observaciones |
|--------|---------|-----------|-----------|---------------|
| Qwen 3B | 4-bit | ~40-50 | ~10-15 | Corre entero en GPU, ideal |
| Mistral 7B | 4-bit | ~15-20 (parcial) | ~4-5 | GPU + RAM, perfectamente usable |
| Mixtral 8x7B | 4-bit | ~2-3 | ~1 | Muy lento, solo CPU |

## Configuración para repartir entre GPU y RAM

    bash
    # Mistral 7B: 20 capas en GPU, 13 en RAM
    ./main -m mistral-7b-instruct.Q4_K_M.gguf -ngl 20

> -ngl = número de capas en GPU. Si ponés 0, todo en CPU. Si ponés un número alto, intenta meter todo en GPU (si no entra, usa RAM).

### ¿Vale la pena?

Sí:

- Privacidad total (nada sale de tu máquina)
- Gratis (sin suscripciones)
- Offline (funciona sin internet)
- Control (vos decidís qué modelo, cuántas capas en GPU)
- Control sobre lo que responde y cómo (próximo post sobre cómo ayudar al modelo a que responda como vos querés)


### La respuesta, por qué trabajar híbridamente

Los modelos en la nube son más rápidos, inmensamente más grandes y pueden proveer mayor capacidad de análisis que un modelo que corrés localmente, son buenos para charlas generales o hacer un ida y vuelta de ideas así como para ajustes finos.
Los modelos locales te ofrecen completa privacidad e independencia, y una vez hecha la curva (si es que se necesita) sobre los puntos fuertes o débiles de un proyecto x, el modelo local te permite avanzar con tranquilidad y a paso firme en cualquier momento incluso en viaje o cuando la red no es segura.

Links útiles

- [Modelos GGUF en Hugging Face](https://huggingface.co/models?search=gguf)
- [Cómo compilé llama.cpp en Fedora con aceleración AMD Radeon](https://gonareco.github.io/blog/posts/llama-cpp-fedora/)