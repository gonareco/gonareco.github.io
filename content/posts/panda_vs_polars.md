---
title: "Pandas vs Polars: mi experiencia con 2,5 millones de registros"
date: 2026-08-06
tags: ["pandas", "polars", "data-science", "data-analyst", "python", "csv","big-data","etl","performance"]
---

## Cuando Pandas empieza a sufrir
Como analista de datos, siempre se busca el equilibrio entre velocidad de análisis y eficiencia de recursos. Pandas ha sido el caballo de batalla indiscutible en Python durante años, pero al trabajar con datasets de gran volumen, se empiezan a sentir sus limitaciones.

Con datasets de varios millones de filas, Pandas comienza a ponerse lento, por lo que es necesario dar el salto a Polars.

>En este post, comparto mi experiencia comparando Polars y Pandas en un escenario real, midiendo tiempo de ejecución, consumo de memoria y facilidad de uso.
### Configuración de la Prueba
Para que los resultados sean reproducibles y estén correctamente contextualizados, detallo el entorno de pruebas:

| Aspecto | Detalle |
|---------|---------|
| **Procesador** | AMD Ryzen 5 7535HS (12 núcleos) |
| **RAM** | 32 GB |
| **Almacenamiento** | SSD NVMe |
| **Sistema Operativo** | Fedora Linux (actualizado) |
| **Python** | 3.11 |
| **Polars** | 1.43.2 |
| **Pandas** | 3.0.5 |
| **Entorno** | Jupyter Lab / Conda |

### Datos
Para esta prueba, utilicé un dataset estructurado y real de 2,5 millones de filas con columnas demográficas y categóricas (similar a una base de clientes). Por razones de confidencialidad, no puedo compartir el dataset original, pero los resultados son replicables con cualquier dataset de tamaño y estructura similar.
### Dataset de prueba
| Característica| Valor |
|-------|------|
|Formato | CSV|
|Tamaño | 1,64 GB|
|Filas | 2.548.056 |
|Columnas | 41|
|Tipo|Datos demográficos y categóricos|

> Nota: Si querés replicar esta prueba, podés usar cualquier dataset público de tamaño similar (ej. NYC Taxi, US Accidents) o generar un dataset sintético con el código que adjunto al final. Yo tenía este a mano y me servía para el post ;-).

### Escenarios de prueba
Las pruebas se dividieron en tres operaciones fundamentales en el día a día de un analista de datos:

- Carga de Datos (read_csv): Leer el archivo desde el disco.
- Filtrado: Aplicar un filtro simple sobre una columna categórica.
- Agregación (GroupBy): Agrupar por una columna categórica y sumar una columna numérica.

## Resultados obtenidos
### Tiempo de ejecución (Rendimiento)
|Operación|Pandas 3.0.5 (seg)|Polars 1.43.2 (seg) | Mejora (x veces)|
|-------|------|------|-------|
|Carga CSV|40,81|16,62|2,5|
|GroupBy|2,55|0,99|2,6|

<img src="/blog/img/pandavspolar-1.png" alt="PandasvsPolars-1" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">


>**Observación:** Polars es consistentemente más rápido, con una ventaja abismal en el filtrado, lo que la hace una herramienta ideal para análisis interactivos y exploratorios en datasets de varios millones de filas.

|Operación|Pandas 3.0.5 (seg)|Polars 1.43.2 (seg) | Mejora (x veces)|
|-------|------|------|-------|
|Filtrado|0,4291|0,0239|18|

<img src="/blog/img/pandavspolar-2.png" alt="PandasvsPolars-2" style="display: block; margin: 0 auto; max-width: 100%; border: 1px solid #ccc; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">

### ¿Por qué Polars es tan rápido?

1. **Rust vs. C/Python:** Tanto Pandas como Polars exponen una API en Python que el usuario utiliza para interactuar con los datos. La diferencia crucial está en cómo ejecutan el trabajo pesado:
    - **Pandas** tiene su núcleo en C (a través de NumPy y Cython). Cada operación que escribís en Python (como un `groupby` o un `filter`) implica múltiples viajes entre el intérprete de Python y el motor en C. Ese intercambio constante genera **overhead** y ralentiza el procesamiento, especialmente en operaciones secuenciales.
    - **Polars** está escrito en Rust y también expone una API en Python. Cuando le das una instrucción a Polars, el motor Rust toma el control y ejecuta todo el trabajo pesado **de forma autónoma**, minimizando la intervención del intérprete de Python. Esto reduce drásticamente el overhead. Además, Rust permite un control de memoria a bajo nivel y aprovecha el **paralelismo nativo** (todos los núcleos de la CPU) de forma nativa. Creo que acá radica gran parte de la ventaja en datasets grandes.
2. **Apache Arrow:** Polars utiliza un formato de datos columnar en memoria (Arrow). Esto acelera el acceso a los datos y permite operaciones vectorizadas altamente optimizadas.
3. **Evaluación Perezosa (Lazy API):** Polars puede construir un plan de ejecución completo y optimizarlo (predicate pushdown, projection pushdown) antes de tocar los datos. Esto reduce drásticamente la cantidad de datos que se leen y procesan.


### Consumo de Memoria
|Operación | Pandas 3.0.5 (MB) | Polars 1.43.2 (MB) | Diferencia (MB)|
|----------|-------------------|--------------------|----------------|
|Carga CSV| 2.180|2.713| +533 (Polars)|

>**Observación:** En este dataset específico, Pandas fue más eficiente en RAM. Sin embargo, este es un costo fijo de la arquitectura de Polars que se diluye a medida que el dataset crece.

Como vimos en los resultados, Polars usó ~533 MB más que Pandas en la carga inicial. Esto se debe a varios factores:
- Modo Eager: La prueba se realizó en modo eager (inmediato), donde Polars materializa todo el DataFrame en memoria para procesar errores fila por fila (este funcionamiento es *similar* a Pandas). En este modo, la prioridad es la velocidad, no la eficiencia de memoria.
- Sobrecarga inicial de Arrow: Apache Arrow tiene una sobrecarga de memoria inicial mayor que el modelo de objetos de Pandas. Esta sobrecarga es fija y se diluye a medida que el dataset crece. Con 5 millones de filas, el porcentaje de sobrecarga es mucho menor.
- Columnas de texto: Mi dataset tiene muchas columnas de texto, y Arrow puede tener una sobrecarga inicial mayor en este tipo de datos. Para columnas numéricas, la diferencia es menor.

Proyección: Basado en benchmarks de la comunidad y mi propia experiencia, el punto de cruce (donde Polars empieza a usar menos memoria que Pandas) suele estar entre 3 y 4 millones de filas. Con 5 millones de filas, Polars ya sería más eficiente en memoria y mucho más rápido que Pandas.

Aunque el consumo de memoria fue ligeramente superior en este caso, la ventaja en rendimiento es tan abismal que el cambio vale la pena para la mayoría de los proyectos de análisis de datos de mediana a gran escala.

### Tiempo vs Memoria
>Ahora uno podrá decir: *"Gonza, son 24 segundos de diferencia y me está consumiendo 500 MB de RAM de más"*. Tenés razón, pero el valor de Polars está en la acumulación.

|Frecuencia de ejecución|Pandas|Polars|	Ahorro diario|	Ahorro anual|
|-------|-----|-----|-----|-----|
|1 vez al día	|40s	|16s|	24s	|2,4 horas|
|5 veces al día	|200s (3,3 min)	|80s (1,3 min)|	2 min	|10 horas|
|10 veces al día	|400s (6,6 min)	|160s (2,6 min)|	4 min	|20 horas|
|50 veces al día (CI/CD)	|2000s (33 min)	|800s (13 min)	|20 min	| 100 horas|

Cuando laburás con el mismo dataset durante un tiempo, el ahorro se acumula y se traduce en iteraciones, menos tiempo de espera y más productividad.

En EDA, donde hacés múltiples filtros y consultas en una sesión, la **diferencia se siente**. La combinación de una carga más rápida (16s vs 40s) y un filtrado 18 veces más rápido hace que la exploración sea fluida y casi instantánea.

Mi experiencia personal: Pasé de esperar ~5 segundos por consulta en Pandas a ~0.2 segundos en Polars. Esa diferencia, multiplicada por decenas de consultas en una sesión de análisis, convierte una hora de trabajo en 15 minutos.

>Nota:
>
>>El hecho de que Polars sea 18 veces más rápido filtrando no significa que todo tu pipeline se ejecutará 18 veces más rápido. En un pipeline real, el filtrado puede ser solo una parte del proceso; los cuellos de botella suelen estar en la carga/escritura de datos o en transformaciones complejas.

Dicho esto, el ahorro es real y se acumula. La combinación de carga más rápida + filtrado ultrarrápido + groupBy eficiente hace que Polars sea una herramienta muy superior para análisis de datos de mediana a gran escala. Sin hablar de datos que crecen exponencialmente. Eso es tema para otro post.

## Recomendaciones Finales

### Yo iría por Polars si...

- Es un dataset de **+3 millones de filas**.
- El flujo de trabajo involucra **múltiples filtros** y transformaciones complejas.
- El rendimiento es crítico y se necesita reducir el tiempo de ejecución del pipeline ETL.
- Hay que preparar el código para el futuro (la comunidad está migrando hacia Arrow).

### Seguir con Pandas si...

- El dataset es pequeño (**<1M filas**).
- Se necesita usar librerías que aún no son compatibles con Polars.
- Se prefiere una API más consolidada y con más ejemplos en la comunidad.

### Mitos(?)
**Polars siempre más rápido**: En datasets pequeños (<100k filas), la sobrecarga de inicialización de Polars puede hacerlo más lento que Pandas.

**"Polars reemplazará a Pandas en todo"**: Pandas tiene 15 años de ecosistema. Librerías como Scikit-learn, Statsmodels o Seaborn funcionan nativamente con Pandas, no con Polars.

**"Polars es superior para ETL y datos grandes"**: Sí, y la tendencia es clara. Pero aún hay casos donde Pandas es la mejor opción.

## Así lo veo yo

**Polars es una evolución real, nada de *hype*.** En mi prueba con **Pandas 3.0.5** (que ya incluye mejoras significativas) y **Polars 1.43.2**, los resultados fueron contundentes:

- **2,5x más rápido** cargando un CSV de 1.6 GB.
- **18x más rápido** filtrando 2,5 millones de filas.
- **2,6x más rápido** en agregaciones complejas.


### A darle átomos
A continuación las celdas que se pueden correr en Jupyter por si querés hacer pruebas.

>Yo ejecutaría las celdas por separado en un Jupyter y probaría cada una antes de avanzar, en mi experiencia está buenísimo detenerse un momento a pensar por qué suceden algunas cosas.

> **Nota sobre formato**: En las tablas uso coma decimal (formato español). En los bloques de código, Python usa punto decimal por defecto.

### Carga de CSV
```python
import polars as pl
import pandas as pd
import time
import os
import psutil

# Medición de memoria
def get_memory_usage():
    process = psutil.Process(os.getpid())
    return process.memory_info().rss / (1024**2)

ruta_csv = "tu_dataset.csv"

print("="*60)
print("📊 COMPARACIÓN PANDAS vs POLARS")
print("="*60)

# ============================================
# CARGA CON PANDAS
# ============================================
print("\n1️⃣ Cargando con Pandas...")
memoria_antes = get_memory_usage()
start = time.time()

df_pandas = pd.read_csv(
    ruta_csv,
    sep=';',  # Ajustá según tu separador
    encoding='latin-1',
    on_bad_lines='skip',
    low_memory=False
)

tiempo_pandas = time.time() - start
memoria_pandas = get_memory_usage() - memoria_antes
print(f"   ⏱️ {tiempo_pandas:.2f}s")
print(f"   💾 {memoria_pandas:.2f} MB")

# ============================================
# CARGA CON POLARS
# ============================================
print("\n2️⃣ Cargando con Polars...")
memoria_antes = get_memory_usage()
start = time.time()

df_polars = pl.read_csv(
    ruta_csv,
    separator=';',
    encoding='latin-1',
    ignore_errors=True,
    try_parse_dates=False,
    infer_schema_length=10000
)

tiempo_polars = time.time() - start
memoria_polars = get_memory_usage() - memoria_antes
print(f"   ⏱️ {tiempo_polars:.2f}s")
print(f"   💾 {memoria_polars:.2f} MB")

```

### Celdas de prueba de filtrado
```python
# ============================================
# FILTRADO
# ============================================
print("\n3️⃣ Probando filtrado...")
# Ajustá estas variables a tus columnas
columna_filtro = "GENERO"
valor_filtro = "M"

start = time.time()
filtrados_pandas = df_pandas[df_pandas[columna_filtro] == valor_filtro]
tiempo_filtro_pandas = time.time() - start

start = time.time()
filtrados_polars = df_polars.filter(pl.col(columna_filtro) == valor_filtro)
tiempo_filtro_polars = time.time() - start

print(f"   Pandas: {tiempo_filtro_pandas:.4f}s")
print(f"   Polars: {tiempo_filtro_polars:.4f}s")
print(f"   🚀 Polars es {tiempo_filtro_pandas/tiempo_filtro_polars:.1f}x más rápido")

```
### Celda de agrupación
```python
# ============================================
# GROUPBY
# ============================================
print("\n4️⃣ Probando GroupBy...")
columna_categoria = "CIRCUITO"
columna_numerica = "Id"

start = time.time()
grupo_pandas = df_pandas.groupby(columna_categoria)[columna_numerica].count()
tiempo_group_pandas = time.time() - start

start = time.time()
grupo_polars = df_polars.group_by(columna_categoria).agg([pl.col(columna_numerica).count()])
tiempo_group_polars = time.time() - start

print(f"   Pandas: {tiempo_group_pandas:.4f}s")
print(f"   Polars: {tiempo_group_polars:.4f}s")
print(f"   🚀 Polars es {tiempo_group_pandas/tiempo_group_polars:.1f}x más rápido")

```

### Resumen de ejemplo
``` python
# ============================================
# RESUMEN FINAL
# ============================================
print("\n" + "="*60)
print("📊 RESUMEN DE COMPARACIÓN")
print("="*60)
print(f"\n{'Operación':<15} {'Pandas':>15} {'Polars':>15} {'Ganador':>15}")
print("-" * 60)
print(f"{'Carga (seg)':<15} {tiempo_pandas:>15.2f} {tiempo_polars:>15.2f} {'Polars' if tiempo_polars < tiempo_pandas else 'Pandas':>15}")
print(f"{'Memoria (MB)':<15} {memoria_pandas:>15.2f} {memoria_polars:>15.2f} {'Polars' if memoria_polars < memoria_pandas else 'Pandas':>15}")
print(f"{'Filtrado (seg)':<15} {tiempo_filtro_pandas:>15.4f} {tiempo_filtro_polars:>15.4f} {'Polars' if tiempo_filtro_polars < tiempo_filtro_pandas else 'Pandas':>15}")
print(f"{'GroupBy (seg)':<15} {tiempo_group_pandas:>15.4f} {tiempo_group_polars:>15.4f} {'Polars' if tiempo_group_polars < tiempo_group_pandas else 'Pandas':>15}")

```

>Nota: Ajustá las variables columna_filtro, valor_filtro, columna_categoria y columna_numerica según las columnas de tu dataset.

### Creación de dataset sintético para pruebas
```python
import polars as pl
import numpy as np
from datetime import datetime, timedelta

print("🔄 Generando dataset sintético...")
n_filas = 2_000_000

# Semillas para reproducibilidad (opcional)
np.random.seed(42)

# Categorías y opciones
categorias = ['Electrónica', 'Ropa', 'Hogar', 'Deportes', 'Libros', 'Juguetes', 'Automotriz']
generos = ['M', 'F']
circuitos = [f'CIRCUITO_{i:03d}' for i in range(1, 51)]
secciones = list(range(1, 101))
profesiones = ['Ingeniero', 'Médico', 'Docente', 'Abogado', 'Comerciante', 'Jubilado', 'Estudiante', 'Administrativo']
estados = ['Activo', 'Inactivo', 'Suspendido']
calles = ['Av. San Martín', 'Calle 25 de Mayo', 'Av. Rivadavia', 'Calle Belgrano', 'Av. Independencia']

# Generar fechas (últimos 10 años)
fecha_base = datetime(2016, 1, 1)
dias_desde_base = (datetime.now() - fecha_base).days
fechas = [fecha_base + timedelta(days=np.random.randint(0, dias_desde_base)) for _ in range(n_filas)]

print("   Generando datos...")
df = pl.DataFrame({
    'id': np.arange(1, n_filas + 1),
    'categoria': np.random.choice(categorias, n_filas),
    'genero': np.random.choice(generos, n_filas, p=[0.48, 0.52]),
    'circuito': np.random.choice(circuitos, n_filas),
    'seccion': np.random.choice(secciones, n_filas),
    'profesion': np.random.choice(profesiones, n_filas),
    'ventas': np.random.uniform(10, 1000, n_filas).round(2),
    'edad': np.random.randint(18, 90, n_filas),
    'estado': np.random.choice(estados, n_filas, p=[0.85, 0.10, 0.05]),
    'fecha_registro': np.random.choice(fechas, n_filas),
    'calle': np.random.choice(calles, n_filas),
    'altura': np.random.randint(1, 5000, n_filas),
    'piso': np.random.choice(['PB'] + [str(i) for i in range(1, 21)], n_filas, p=[0.15] + [0.85/20]*20),
    'departamento': np.random.choice(['A', 'B', 'C', 'D', ''] + [f'{i:02d}' for i in range(1, 51)], n_filas)
})

# Guardar como CSV
print("   Guardando archivo...")
df.write_csv("datos_sinteticos.csv", separator=';')

# Mostrar info del dataset generado
tamaño_mb = df.estimated_size() / (1024**2)
print(f"\n✅ Dataset generado exitosamente:")
print(f"   📊 Filas: {df.height:,}")
print(f"   📋 Columnas: {df.width}")
print(f"   💾 Tamaño estimado: {tamaño_mb:.2f} MB")
print(f"   📁 Archivo: datos_sinteticos.csv")
print(f"\n📋 Estructura de columnas:")
for col, dtype in df.schema.items():
    print(f"   - {col}: {dtype}")

# Mostrar primeras filas como muestra
print("\n🔍 Muestra de los primeros registros:")
print(df.head(5))
```

Si este post te gustó, el próximo te va a encantar.

Links útiles
- [Pandas-vs-Polars benchmark](https://github.com/AjayBhonsle/pandas_polars_benchmark)
- [Polars User Guide](https://docs.pola.rs/)
- [Polars Docs](https://pola.rs/)
- [Pandas User Guide](https://pandas.pydata.org/docs/user_guide/index.html)