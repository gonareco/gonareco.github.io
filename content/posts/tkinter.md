---
title: "Cómo normalicé 40.000 direcciones con un 99.5% de precisión"
date: 2026-05-13
draft: false
tags: ["Python", "Pandas", "Tkinter", "Regex", "Data Cleaning"]
---

## El problema real

En un proyecto para el **IDECBA**, el **Instituto de Estadísticas y Censos de la Ciudad de Buenos Aires**, se necesitaba normalizar ~40.000 direcciones por lote.

¿El problema? Estaban escritas de formas inconsistentes, con direcciones codificadas y datos crudos.

| Entrada original |
|------------------|
| "Av. Rivadavia 1234 piso 3" |
| "Rivadavia 1234" |
| "Av Rivadavia 1234" |
| "av Rivadavia1234" |
| 10430 3686 |
| 7075 119 |
| 1675 1975 |
| Chilavert y Corvalan-mz. 21 casa 129 0 |

El objetivo era extraer **calle** y **altura** para cruzar con otras bases poblacionales ya estandarizadas.

Estas direcciones fueron cargadas a mano en su momento, por lo que naturalmente había algunas inconsistencias por la propia naturaleza de la carga de los datos.

El trabajo era manual y consistía en revisar línea por línea cada uno de los casos y mientras se verificaba el nombre correcto de cada calle según el conocimiento de la persona que lo realizaba.

Se necesitaba de manera **urgente** un script que diera una solución y dentro de un flujo de trabajo ya establecido y permitiera a usuarios no técnicos el uso del aplicativo de manera independiente.

## Decisiones

### Por qué no usé una API externa

- Los datos eran sensibles (no podían salir de la red interna)
- Necesitaba procesamiento offline
- El equipo usuario no era técnico

### ¿Por qué regex y no NLP?

- Ventajas
  - Control total
  - Velocidad
  - Sin dependencias externas
- Desventajas
  - Frágil ante cambios no previstos

La inmediatez y el control total me inclinaron por el uso de regex. (Lo viejo funciona, Juan.)

## La solución: expresiones regulares + Pandas + Tkinter

### Para las direcciones codificadas
```python
if re.match(r'^\d{3,5}\s+\d{1,5}(?:\s|$)', direccion):
    partes = re.split(r'\s+', direccion, maxsplit=2)
    calle, altura = partes[0], partes[1]
```
Ejemplo:"10430 3686" -> calle: "10430", altura: "3686"

### 1. El corazón del algoritmo

```python
def separar_direccion(self, direccion):
    # Normalización básica
    direccion = re.sub(r'\s+', ' ', direccion.strip())
    direccion = re.sub(r'[/\-.,]', ' ', direccion)
    
    # Caso principal: "texto + número"
    if re.match(r'^[^\d]+\s+\d{1,5}', direccion, re.IGNORECASE):
        match = re.match(r'^(.*?)\s+(\d{1,5})\s*(.*)$', direccion)
        if match:
            calle = match.group(1).strip()
            altura = match.group(2).strip()
```
Ejemplo: "Av. Rivadavia 1234 piso 3" → calle: "Av. Rivadavia", altura: "1234".

### 2. Manejo de casos complejos (Casos para revisión manual)

```python
elif any(palabra in direccion.lower() for palabra in ['calle','barrio','manzana','mzn','mza','manz','mz','mzna','casa','galpon','villa']):
    sinsep = direccion  # Marcar para revisión manual
```

Ejemplo: "Chilavert y Corvalan-mz. 21 casa 129 0" → no separable automáticamente.

> Fallback: sinsep
>
> Los casos no separados (~0.5% de los 40.000, unas 200 direcciones por lote) se marcaban en una columna sinsep para revisión manual posterior por el equipo.


### 3. La interfaz: Tkinter

Desarrollé una interfaz gráfica simple pero funcional:
```
Selección de archivo CSV
Barra de progreso (clave para lotes grandes)
Mensajes de estado en tiempo real
Exportación con columnas adicionales: calle, altura, resto, sinsep, condsep
```


<img src="/blog/img/tkinter-ui.png" alt="Interfaz" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

### 4. Resultados


| Métrica | Valor |
|---------|-------|
| Registros por lote | ~40.000 |
| Precisión | 99.5% (∼200 errores por lote) |
| Tiempo de procesamiento | 1-3 segundos |
| Errores | Revisión manual posterior |

### Lecciones aprendidas

1. Las regex bien diseñadas son suficientes para normalización de direcciones. No necesitás NLP complejo.

2. El fallback es clave: Siempre dejá un campo sinsep para revisión manual de casos no previstos.

3. La interfaz importa: Tkinter permitía que cualquier usuario pudiera ejecutar el script sin tocar la terminal.

### Código completo

Disponible en GitHub:
[github.com/gonareco/direcciones-normalizador](https://github.com/gonareco/direcciones-normalizador)

### Tecnologías usadas
* Python 3

* Pandas (procesamiento masivo)

* Tkinter (interfaz gráfica)

* Expresiones regulares (extracción de patrones)
