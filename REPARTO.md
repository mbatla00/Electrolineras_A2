# Reparto de Tareas — Electrolineras A2

> Matemática Finita II — 2025/2026
>
> Corredor: **A-2** (Madrid – Zaragoza – Barcelona)

---

## 📋 Resumen

| Pareja | Integrantes | Responsabilidad | Entregable principal |
|:------:|-------------|-----------------|----------------------|
| **1** | María, Sofía | Formulación matemática y análisis de complejidad | Secciones 1-3 del informe |
| **2** | ???, ??? | Diseño algorítmico e implementación | Notebooks con ILP y heurística |
| **3** | ???, ??? | Datos, grafos, árboles, flujos y visualización | Notebooks con grafo, MST, flujo y mapas |

---

## 📅 Calendario (ORIENTATIVO, es para el flujo de trabajo)

| Día | Pareja 1 | Pareja 2 | Pareja 3 |
|:---:|----------|----------|----------|
| **1** | Leer PDF, empezar definición formal | Configurar PuLP, prototipo ILP | Cargar shapefiles, filtrar A-2 |
| **2** | Terminar FO + restricciones | Implementar heurístico voraz | Crear candidatos, grafo, matriz distancias |
| **3** | Pasar parámetros a Pareja 2 | ILP con datos reales | **Entregar** tramos.csv, candidatos.csv, matriz_distancias.npy |
| **4** | Redactar análisis de complejidad | Depurar ILP, comparar | MST y red de flujo |
| **5** | Casos polinomiales, terminar sección | Tablas y gráficos comparativos | Visualizaciones finales |
| **6** | **PUESTA EN COMÚN** | **PUESTA EN COMÚN** | Recibir solución óptima para visualizar |
| **7** | Revisión cruzada | Revisión cruzada | Revisión cruzada |
| **8** | **ENTREGA** | **ENTREGA** | **ENTREGA** |

---

## Pareja 1 — Formulación Matemática y Análisis de Complejidad

**Objetivo:** Redactar las secciones 1, 2 y 3 del informe y demostrar la complejidad computacional del problema.

### Tareas

#### 1.1. Definición formal del problema

A partir de la Propuesta 2 del PDF, definir con notación matemática rigurosa:

**Conjuntos:**

- `C = {c_1, c_2, ..., c_m}` — ubicaciones candidatas para instalar electrolineras (áreas de servicio existentes + nuevas ubicaciones en tramos sin cobertura)
- `T = {t_1, t_2, ..., t_n}` — tramos en que se divide la A-2 (segmentos entre salidas)
- `V` — tipos de vehículo según autonomía (estándar 300 km, extendida 500 km)

**Parámetros (con unidades y fuentes):**

| Parámetro | Descripción | Fuente |
|-----------|-------------|--------|
| `d_i` | Demanda diaria de recargas en el tramo `i` (vehículos/día) | `IMD_lig` del shapefile |
| `l_i` | Longitud del tramo `i` (km) | Shapefile |
| `cap_j` | Número máximo de puntos de recarga en ubicación `j` (2–6) | PDF |
| `R` | Autonomía de referencia (350 km) | Supuesto |
| `D_max = 245 km` | Distancia máxima entre electrolineras (margen 30%) | Cálculo |
| `f_j` | Coste fijo de instalación en `j` (€) | Supuesto |
| `dist(i,j)` | Distancia del centroide del tramo `i` a la ubicación `j` (km) | Cálculo (Pareja 3) |

**Variables de decisión:**

- `x_j ∈ {0, 1}` — 1 si se instala electrolinera en `j`
- `y_{ij} ∈ {0, 1}` — 1 si el tramo `i` se asigna a la electrolinera `j`

#### 1.2. Función objetivo
```math
\min Z = \sum_{j \in C} (f_j + o_j) \cdot x_j
```

#### 1.3. Restricciones

| # | Nombre | Fórmula |
|---|--------|---------|
| R1 | Cobertura obligatoria | `Σ_{j: dist(i,j) ≤ D_max} x_j ≥ 1, ∀i ∈ T` |
| R2 | Asignación coherente | `y_{ij} ≤ x_j` |
| R3 | Capacidad máxima | `Σ_i d_i · y_{ij} ≤ cap_j · 30` |
| R4 | Redundancia por sentido | `Σ_{j: dist(i,j) ≤ D_max} x_j ≥ 2, ∀i ∈ T` |
| R5 | Equidad territorial | `Σ_{j ∈ C_k} x_j ≥ 1, ∀k ∈ K_rural` |
| R6 | Separación mínima (30 km) | `x_j + x_l ≤ 1` si `dist(j,l) < 30 km` |
| R7 | Variables binarias | `x_j, y_{ij} ∈ {0,1}` |

#### 1.4. Análisis de complejidad computacional

**Demostración de NP-completitud:**

1. **Problema de decisión:** "¿Existe `S ⊆ C` con `|S| ≤ k` que cubra todos los tramos?"

2. **Reducción desde SET COVER:**
   - Universo `U` → tramos `T`
   - Colección `𝒮` → ubicaciones `C`
   - `u_i ∈ S_j` ⇔ `dist(t_i, c_j) ≤ D_max`
   - Mismo `k`

3. **Pertenencia a NP:** verificación `O(|T| · |S|)`, polinomial.

4. **Conclusión:** NP-completo.

**Casos polinomiales:**

- **Topología lineal:** La A-2 es una línea → algoritmo voraz óptimo en `O(n log n)`.
- **k fijo (≤ 10):** Fuerza bruta `O(|C|^k)` aceptable.

#### 1.5. Entregable

- Secciones 1-3 del informe en LaTeX o Word
- Pseudocódigo del algoritmo voraz para el caso lineal

---

## Pareja 2 — Diseño Algorítmico e Implementación Computacional

**Objetivo:** Implementar y comparar dos estrategias algorítmicas contrastadas (exacta y heurística), documentando pseudocódigo, complejidad y calidad de solución.

### Paso 2.1 — Recepción de datos de la Pareja 3

Antes del Día 3, la Pareja 3 os entrega:

- `tramos.csv` — columnas: `id`, `longitud`, `demanda_diaria`, `coordenadas_centroide`
- `candidatos.csv` — columnas: `id`, `coste_fijo`, `capacidad`, `coordenadas`
- `matriz_distancias.npy` — matriz `|T| × |C|` con distancias en km
- `D_max = 245` km

### Paso 2.2 — Enfoque exacto: Programación Entera (ILP) con PuLP

```python
from pulp import *
import pandas as pd
import numpy as np

# Cargar datos
tramos_df = pd.read_csv('tramos.csv')
candidatos_df = pd.read_csv('candidatos.csv')
dist_matrix = np.load('matriz_distancias.npy')

T = range(len(tramos_df))
C = range(len(candidatos_df))
D_max = 245

demanda = tramos_df['demanda_diaria'].values
coste_fijo = candidatos_df['coste_fijo'].values
capacidad = candidatos_df['capacidad'].values

# Modelo ILP
prob = LpProblem("Electrolineras_A2", LpMinimize)

# Variables
x = {j: LpVariable(f"x_{j}", cat='Binary') for j in C}
y = {(i, j): LpVariable(f"y_{i}_{j}", cat='Binary') for i in T for j in C}

# Función objetivo: minimizar coste total
prob += lpSum(coste_fijo[j] * x[j] for j in C)

# R1: Cobertura (cada tramo cubierto por ≥ 1 estación)
for i in T:
    prob += lpSum(x[j] for j in C if dist_matrix[i, j] <= D_max) >= 1

# R2: Asignación coherente
for i in T:
    for j in C:
        prob += y[(i, j)] <= x[j]

# R3: Capacidad (máx 30 recargas/día/punto)
for j in C:
    prob += lpSum(demanda[i] * y[(i, j)] for i in T) <= capacidad[j] * 30

# R4: Redundancia (≥ 2 estaciones por tramo)
for i in T:
    prob += lpSum(x[j] for j in C if dist_matrix[i, j] <= D_max) >= 2

# Resolver (límite 5 min)
prob.solve(PULP_CBC_CMD(msg=True, timeLimit=300))

print(f"Estado: {LpStatus[prob.status]}")
print(f"Coste total: {value(prob.objective):,.0f} €")
print(f"Estaciones: {[j for j in C if value(x[j]) == 1]}")
```

### Paso 2.3 — Enfoque heurístico: Algoritmo Voraz
```python
def voraz_cobertura_autopista(T, C, demanda, coste_fijo, dist_matrix, D_max):
    """
    Algoritmo voraz para ubicación de electrolineras.
    Ratio de aproximación: H(Δ) donde Δ = max demanda cubierta por una estación.
    """
    S = []
    cubierto = np.zeros(len(T), dtype=bool)
    
    while not cubierto.all():
        mejor_j = None
        mejor_ratio = -1
        
        for j in C:
            if j in S:
                continue
            tramos_j = [i for i in T if dist_matrix[i, j] <= D_max and not cubierto[i]]
            demanda_nueva = sum(demanda[i] for i in tramos_j)
            ratio = demanda_nueva / coste_fijo[j] if coste_fijo[j] > 0 else float('inf')
            
            if ratio > mejor_ratio:
                mejor_ratio = ratio
                mejor_j = j
        
        if mejor_j is None:
            break
        
        S.append(mejor_j)
        for i in T:
            if dist_matrix[i, mejor_j] <= D_max:
                cubierto[i] = True
    
    return S

S_heuristico = voraz_cobertura_autopista(T, C, demanda, coste_fijo, dist_matrix, D_max)
```

### Paso 2.4 — Análisis de complejidad temporal

| Algoritmo | Complejidad | Correctitud |
|-----------|-------------|-------------|
| ILP (Branch & Bound) | `O(2^\|C\|)` peor caso | Óptimo global |
| Voraz | `O(\|C\|² · \|T\|)` | Ratio `H(Δ) ≤ ln Δ + 1` |

---

### Paso 2.5 — Comparación experimental

Ejecutar ambos algoritmos con:

- Instancia real A-2 (≈ 50-100 tramos, 20-30 candidatos)
- Instancias sintéticas más grandes (100, 200, 500 tramos)

**Métricas a comparar:**

1. Tiempo de ejecución (s)
2. Coste total (€)
3. Gap: `(Z_heur - Z_opt) / Z_opt · 100%`
4. Número de estaciones
5. Cobertura de demanda (%)

**Tabla esperada:**

| Instancia | n | m | Tiempo ILP | Tiempo Voraz | Coste ILP | Coste Voraz | Gap |
|-----------|---|---|------------|--------------|-----------|-------------|-----|
| A-2 real | 60 | 25 | 45.2 s | 0.03 s | 2.450.000 € | 2.680.000 € | 9.4% |
| Sintética | 200 | 50 | >600 s | 0.12 s | — | 8.900.000 € | — |

---

### Paso 2.6 — Entregable

Notebooks Jupyter:

- `02_algoritmo_exacto.ipynb`
- `03_algoritmo_heuristico.ipynb`

Contenido de cada uno:

1. Carga de datos
2. Implementación del algoritmo
3. Pseudocódigo en celdas Markdown
4. Ejecución y resultados
5. Tablas y gráficos comparativos
6. Análisis de sensibilidad (variando `D_max`, capacidades, costes)

---

## Pareja 3 — Datos, Modelado con Grafos, Árboles, Flujos y Visualización

**Objetivo:** Procesar los shapefiles, construir el grafo de la A-2, aplicar algoritmos de grafos (caminos mínimos, MST, flujo máximo), generar las visualizaciones y proporcionar los datos procesados a las otras parejas.

---

### Paso 3.1 — Carga de shapefiles

```python
import geopandas as gpd
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import networkx as nx
from shapely.geometry import Point
from scipy.spatial.distance import cdist

# Cargar
red = gpd.read_file("datos/250717_IMD2024_CatRCE2024.shp")
aforos = gpd.read_file("datos/250717 Estaciones2024_IMD.shp")

# Inspeccionar
print(red.columns.tolist())
print(red.head(2))
```

### Paso 3.2 — Filtrar la A-2
```python
# Explorar valores únicos del campo de código/nombre de vía
print(red.iloc[:, 0].unique()[:30])

# Filtrar la A-2 (probable código: 'A-2', 'E-90', 'Autovía del Nordeste')
mascara = red['codigo'].str.contains('A-2|A2|E-90|AUTOVIA DEL NORDESTE', case=False, na=False)
gdf_A2 = red[mascara].copy()

print(f"Tramos de la A-2: {len(gdf_A2)}")

# Si hay pocos tramos, inspeccionar más columnas
if len(gdf_A2) < 20:
    print("Valores únicos del campo de vía:")
    for col in red.columns:
        if red[col].dtype == 'object':
            muestra = red[col].dropna().unique()[:20]
            print(f"  {col}: {muestra}")
```

### Paso 3.3 — Limpieza y preparación
```python
# Renombrar columnas
gdf_A2 = gdf_A2.rename(columns={
    'IMD': 'IMD_total',
    'IMD_lig': 'IMD_ligeros',
    'longitud': 'longitud_km',
    'codigo': 'codigo_via'
})

# Convertir a km si está en metros
if gdf_A2['longitud_km'].max() > 1000:
    gdf_A2['longitud_km'] = gdf_A2['longitud_km'] / 1000

# Demanda estimada: 5% de vehículos ligeros son eléctricos y necesitan recarga en ruta
gdf_A2['demanda_recarga'] = gdf_A2['IMD_ligeros'] * 0.05

print(gdf_A2[['codigo_via', 'IMD_total', 'IMD_ligeros', 'longitud_km', 'demanda_recarga']].head(10))
```

### Paso 3.4 — Crear ubicaciones candidatas
```python
candidatos = []
for idx, row in gdf_A2.iterrows():
    line = row.geometry
    midpoint = line.interpolate(0.5, normalized=True)
    candidatos.append({
        'id': f"C_{idx}",
        'geometry': midpoint,
        'tipo': 'existente' if row['IMD_total'] > 20000 else 'nuevo',
        'coste_fijo': 150000 if row['IMD_total'] > 20000 else 300000,
        'capacidad': 6 if row['IMD_total'] > 20000 else 4
    })

gdf_candidatos = gpd.GeoDataFrame(candidatos, crs=gdf_A2.crs)
gdf_candidatos.to_file("outputs/candidatos_A2.geojson", driver='GeoJSON')
```

### Paso 3.5 — Construcción del grafo con NetworkX
```python
G = nx.Graph()

for idx, row in gdf_A2.iterrows():
    coords = list(row.geometry.coords)
    nodo_i = (round(coords[0][0], 5), round(coords[0][1], 5))
    nodo_f = (round(coords[-1][0], 5), round(coords[-1][1], 5))
    
    G.add_node(nodo_i, x=nodo_i[0], y=nodo_i[1])
    G.add_node(nodo_f, x=nodo_f[0], y=nodo_f[1])
    G.add_edge(nodo_i, nodo_f,
               longitud=row['longitud_km'],
               IMD=row['IMD_total'],
               IMD_ligeros=row['IMD_ligeros'],
               demanda=row['demanda_recarga'],
               tramo_id=idx)

print(f"Grafo A-2: {G.number_of_nodes()} nodos, {G.number_of_edges()} aristas")
print(f"¿Es conexo?: {nx.is_connected(G)}")

# Guardar grafo
nx.write_graphml(G, "outputs/A2_grafo.graphml")
```

### Paso 3.6 — Cálculo de la matriz de distancias ⚠️ ENTREGAR A PAREJA 2 EL DÍA 3
# Centroides de tramos
```python
gdf_A2['centroide'] = gdf_A2.geometry.centroid
coords_tramos = np.array([[p.x, p.y] for p in gdf_A2['centroide']])

# Coordenadas de candidatos
coords_candidatos = np.array([[p.x, p.y] for p in gdf_candidatos.geometry])

# Matriz euclídea con factor de corrección
dist_matrix = cdist(coords_tramos, coords_candidatos) * 111.32  # grados → km
dist_matrix = dist_matrix * 1.3  # factor de ruta por curvatura

np.save("outputs/matriz_distancias.npy", dist_matrix)
print(f"Matriz de distancias: {dist_matrix.shape}")

# Exportar CSVs
gdf_A2[['codigo_via', 'longitud_km', 'IMD_ligeros', 'demanda_recarga']].to_csv("outputs/tramos.csv", index_label='id')
gdf_candidatos[['id', 'coste_fijo', 'capacidad', 'tipo']].to_csv("outputs/candidatos.csv", index=False)
```

### Paso 3.7 — Archivos a entregar a las otras parejas

| Archivo | Contenido | Para |
|---------|-----------|------|
| `tramos.csv` | ID, longitud_km, demanda_recarga, IMD_ligeros | Pareja 1 y 2 |
| `candidatos.csv` | ID, coste_fijo, capacidad, tipo | Pareja 1 y 2 |
| `matriz_distancias.npy` | Matriz \|T\| × \|C\| en km | Pareja 2 |
| `A2_grafo.graphml` | Grafo NetworkX completo | Interno |

---

### Paso 3.8 — Árbol Recubridor Mínimo (MST)

```python
G_candidatos = nx.Graph()
for i, c1 in gdf_candidatos.iterrows():
    G_candidatos.add_node(i, pos=(c1.geometry.x, c1.geometry.y))
    for j, c2 in gdf_candidatos.iterrows():
        if i < j:
            dist = np.sqrt((c1.geometry.x - c2.geometry.x)**2 + 
                          (c1.geometry.y - c2.geometry.y)**2) * 111.32
            G_candidatos.add_edge(i, j, weight=dist)

mst = nx.minimum_spanning_tree(G_candidatos)
print(f"MST: {mst.number_of_nodes()} nodos, {mst.number_of_edges()} aristas")
```

**Justificación para el informe:** El MST minimiza la infraestructura de conexión eléctrica entre estaciones, reduciendo el coste total de despliegue al compartir transformadores y líneas de media tensión.

---

### Paso 3.9 — Red de flujo

```python
G_flujo = nx.DiGraph()

# Nodo fuente y sumidero
G_flujo.add_node('MADRID', tipo='origen')
G_flujo.add_node('BARCELONA', tipo='destino')

# Nodos intermedios = electrolineras
for j, row in gdf_candidatos.iterrows():
    G_flujo.add_node(f"E_{j}", capacidad=row['capacidad'] * 30, tipo='estacion')

# Aristas con capacidad = flujo máximo de VE entre estaciones consecutivas
# Implementar algoritmo de flujo máximo (Ford-Fulkerson o nx.maximum_flow)

print(f"Red de flujo: {G_flujo.number_of_nodes()} nodos, {G_flujo.number_of_edges()} aristas")
```

### Paso 3.10 — Visualizaciones para el informe
#### Mapa 1: IMD a lo largo de la A-2
```python
fig, ax = plt.subplots(figsize=(14, 6))
gdf_A2.plot(ax=ax, column='IMD_ligeros', cmap='YlOrRd', linewidth=2, legend=True)
gdf_candidatos.plot(ax=ax, color='blue', markersize=20, marker='s', label='Candidatos')
ax.set_title('IMD de vehículos ligeros en la A-2 con ubicaciones candidatas')
plt.tight_layout()
plt.savefig('outputs/imd_A2.png', dpi=300)
```

#### Mapa 2: Solución final con estaciones seleccionadas
```python
# Después de recibir la solución de la Pareja 2
seleccionadas = gdf_candidatos.iloc[solucion_optima]

fig, ax = plt.subplots(figsize=(14, 6))
gdf_A2.plot(ax=ax, color='gray', linewidth=1)
gdf_candidatos.plot(ax=ax, color='lightblue', markersize=30, marker='s', 
                    alpha=0.5, label='No seleccionada')
seleccionadas.plot(ax=ax, color='red', markersize=50, marker='*', 
                   label='Seleccionada')

# Radios de cobertura
for _, row in seleccionadas.iterrows():
    circle = plt.Circle((row.geometry.x, row.geometry.y), 
                        D_max/111.32, color='red', alpha=0.1)
    ax.add_patch(circle)

ax.set_title('Solución: electrolineras seleccionadas y radios de cobertura')
plt.legend()
plt.tight_layout()
plt.savefig('outputs/solucion_A2.png', dpi=300)
```
### Paso 3.11 — Entregable de la Pareja 3

Notebooks Jupyter:

- `01_carga_datos.ipynb`
- `04_visualizaciones.ipynb`

Contenido:

1. Carga y filtrado de shapefiles
2. Creación de candidatos
3. Construcción del grafo NetworkX
4. Cálculo de matriz de distancias
5. MST y análisis
6. Red de flujo
7. **Todas** las visualizaciones del informe
8. Exportación de datos para las otras parejas

**Archivos para el informe PDF:**

- `imd_A2.png`
- `solucion_A2.png`
- `mst_A2.png`
- `flujo_A2.png`
