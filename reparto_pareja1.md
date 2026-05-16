## Pareja 1 — Formulación Matemática y Análisis de Complejidad

**Objetivo:** Redactar las secciones 1, 2 y 3 del informe y demostrar la complejidad computacional del problema.

---

### Paso 1.1 — Definición formal del problema

A partir de la Propuesta 2 del PDF (páginas 3-4), definir con notación matemática rigurosa:

#### Conjuntos

- `C = {c_1, c_2, ..., c_m}` — ubicaciones candidatas para instalar electrolineras (áreas de servicio existentes + nuevas ubicaciones en tramos sin cobertura)
- `T = {t_1, t_2, ..., t_n}` — tramos en que se divide la A-2 (segmentos entre salidas o cada 10-20 km)
- `V` — tipos de vehículo según autonomía (estándar 300 km, extendida 500 km), simplificado a una autonomía de referencia

#### Parámetros (con unidades y fuentes)

| Parámetro | Descripción | Unidad | Fuente |
|-----------|-------------|--------|--------|
| `d_i` | Demanda diaria de recargas en el tramo `i` | vehículos/día | `IMD_lig` del shapefile `250717_IMD2024_CatRCE2024.shp` |
| `l_i` | Longitud del tramo `i` | km | Shapefile |
| `cap_j` | Número máximo de puntos de recarga instalables en la ubicación `j` | puntos (2–6) | PDF (Propuesta 2) |
| `R` | Autonomía de referencia del vehículo eléctrico | km | Supuesto: 350 km (valor medio) |
| `D_max` | Distancia máxima entre electrolineras consecutivas | km | `R · (1 - 0.10 - 0.20) = 245 km` (margen seguridad 30%) |
| `f_j` | Coste fijo de instalación en la ubicación `j` | € | Supuesto: 150.000 € (existente) / 300.000 € (nuevo) |
| `o_j` | Coste operativo anual de la ubicación `j` | €/año | Supuesto: 10% del coste fijo |
| `dist(i, j)` | Distancia del centroide del tramo `i` a la ubicación `j` | km | Calculado por Pareja 3 |
| `pob_k` | Población de la zona rural `k` cercana a la A-2 | habitantes | INE |
| `ρ` | Número medio de recargas diarias por punto | recargas/día | Supuesto: 30 |

#### Variables de decisión

- `x_j ∈ {0, 1}` — 1 si se instala una electrolinera en la ubicación `j`, 0 en caso contrario
- `y_{ij} ∈ {0, 1}` — 1 si el tramo `i` se asigna a la electrolinera `j`, 0 en caso contrario

---

### Paso 1.2 — Función objetivo

**Objetivo principal:** Minimizar el coste total de instalación y operación.

```math
\min Z = \sum_{j \in C} (f_j + o_j) \cdot x_j
```
**Objetivo secundario (o restricción):** Maximizar la cobertura de demanda.
```math
\max \sum_{i \in T} \sum_{j \in C} d_i \cdot y_{ij}
```
**Justificación:** Se prioriza la minimización del coste porque el presupuesto es limitado (autosostenibilidad), pero se garantiza como restricción fuerte la cobertura de seguridad (ningún punto de la A-2 puede estar a más de `D_max` km de una electrolinera).

---

### Paso 1.3 — Restricciones

| # | Nombre | Fórmula | Explicación |
|---|--------|---------|-------------|
| **R1** | Cobertura obligatoria | `Σ_{j ∈ C : dist(i,j) ≤ D_max} x_j ≥ 1, ∀i ∈ T` | Cada tramo debe tener al menos una electrolinera a distancia ≤ `D_max` |
| **R2** | Asignación coherente | `y_{ij} ≤ x_j, ∀i ∈ T, j ∈ C` | Un tramo solo puede asignarse a una electrolinera si esta está instalada |
| **R3** | Capacidad máxima | `Σ_{i ∈ T} d_i · y_{ij} ≤ cap_j · ρ, ∀j ∈ C` | La demanda asignada no puede superar la capacidad de recarga diaria de la estación |
| **R4** | Redundancia por sentido | `Σ_{j ∈ C : dist(i,j) ≤ D_max} x_j ≥ 2, ∀i ∈ T` | Cada tramo debe estar cubierto por al menos 2 estaciones (una por sentido de marcha o fallo) |
| **R5** | Equidad territorial | `Σ_{j ∈ C_k} x_j ≥ 1, ∀k ∈ K_rural` | Los municipios rurales atravesados deben tener cobertura en un radio de 20 km |
| **R6** | Separación mínima | `x_j + x_l ≤ 1, ∀j,l ∈ C : dist(j,l) < 30 km` | Evitar canibalización de demanda entre estaciones demasiado cercanas |
| **R7** | Variables binarias | `x_j ∈ {0,1}, y_{ij} ∈ {0,1}` | Naturaleza de las variables de decisión |

---

### Paso 1.4 — Análisis de complejidad computacional

#### Demostración de NP-completitud

**Problema de decisión asociado:**

> Dados un conjunto `C` de ubicaciones candidatas, un conjunto `T` de tramos, una distancia máxima `D_max` y un entero `k`, ¿existe un subconjunto `S ⊆ C` con `|S| ≤ k` tal que todo tramo `i ∈ T` esté a distancia `≤ D_max` de al menos un elemento de `S`?

**Reducción desde SET COVER:**

1. **SET COVER** (problema NP-completo canónico):
   - Universo `U = {u_1, u_2, ..., u_n}`
   - Colección de subconjuntos `𝒮 = {S_1, S_2, ..., S_m}` con `S_j ⊆ U`
   - Entero `k`
   - Pregunta: ¿Existe una subcolección `𝒞 ⊆ 𝒮` con `|𝒞| ≤ k` tal que `⋃_{S ∈ 𝒞} S = U`?

2. **Construcción de la instancia de nuestro problema:**
   - Cada elemento `u_i ∈ U` → tramo `t_i ∈ T`
   - Cada subconjunto `S_j ∈ 𝒮` → ubicación candidata `c_j ∈ C`
   - `u_i ∈ S_j` ⇔ `dist(t_i, c_j) ≤ D_max`
   - Mismo valor de `k`

3. **Demostración de equivalencia:**
   - **(⇒)** Si existe un SET COVER de tamaño `k`, las ubicaciones correspondientes cubren todos los tramos por construcción.
   - **(⇐)** Si existe un conjunto de `k` ubicaciones que cubren todos los tramos, los subconjuntos correspondientes forman un SET COVER de `U`.

4. **Pertenencia a NP:**
   - Dado un conjunto `S`, verificar que cubre todos los tramos (comprobar `∀i, ∃j ∈ S : dist(i,j) ≤ D_max`) se hace en tiempo `O(|T| · |S|)`, que es polinomial en el tamaño de la entrada.

**Conclusión:** El problema es **NP-completo** (pertenece a NP y es NP-hard por reducción desde SET COVER).

#### Casos polinomiales identificables

**Caso 1: Topología lineal (autopista sin ramales significativos).**

La A-2 es esencialmente una línea. En grafos de intervalos en 1D, el problema de cobertura se resuelve con un **algoritmo voraz óptimo** en tiempo `O(n log n)`:
```text
Algoritmo CoberturaLineal(T, C, D_max):
    Ordenar candidatos C y tramos T de izquierda a derecha
    S = ∅
    i = 0  // índice del primer tramo no cubierto
    mientras i < |T|:
        elegir j* = candidato más a la derecha que cubra t_i
        S = S ∪ {j*}
        i = primer tramo no cubierto por j*
    devolver S
```


**Demostración de optimalidad:** Por intercambio. Dada una solución óptima `S*`, si el primer candidato seleccionado por el voraz `j_1` no está en `S*`, se puede reemplazar el primer candidato de `S*` por `j_1` sin pérdida de cobertura (porque `j_1` es el que más a la derecha cubre `t_1`).

**Caso 2: Número fijo de estaciones (`k` pequeño).**

Si el presupuesto solo permite `k ≤ 10` estaciones, la fuerza bruta `O(|C|^k)` es aceptable.

---

### Paso 1.5 — Formulación matemática completa

```math
\begin{aligned}
\min \quad & Z = \sum_{j \in C} (f_j + o_j) \cdot x_j \\
\text{s.a.} \quad & \sum_{j \in C : dist(i,j) \leq D_{max}} x_j \geq 1, && \forall i \in T \quad &\text{(R1: Cobertura)} \\
& y_{ij} \leq x_j, && \forall i \in T, j \in C \quad &\text{(R2: Asignación)} \\
& \sum_{i \in T} d_i \cdot y_{ij} \leq cap_j \cdot \rho, && \forall j \in C \quad &\text{(R3: Capacidad)} \\
& \sum_{j \in C : dist(i,j) \leq D_{max}} x_j \geq 2, && \forall i \in T \quad &\text{(R4: Redundancia)} \\
& \sum_{j \in C_k} x_j \geq 1, && \forall k \in K_{rural} \quad &\text{(R5: Equidad)} \\
& x_j + x_l \leq 1, && \forall j,l \in C : dist(j,l) < 30 \quad &\text{(R6: Separación)} \\
& x_j \in \{0, 1\}, && \forall j \in C \quad &\text{(R7: Binaria)} \\
& y_{ij} \in \{0, 1\}, && \forall i \in T, j \in C \quad &\text{(R7: Binaria)}
\end{aligned}
```
### Paso 1.6 — Entregable de la Pareja 1

Redactar las siguientes secciones del **informe final conjunto** (siguiendo el formato del PDF de la asignatura: portada, índice, introducción, desarrollo, conclusiones, referencias, anexos):

| Sección | Contenido | Responsable |
|---------|-----------|:----------:|
| **Portada** | Institución, título, autoría (los 6), asignatura, fecha | Pareja 1 |
| **Índice** | General + tablas y figuras | Pareja 1 |
| **1. Introducción** | Objetivo, justificación, metodología general | Pareja 1 |
| **2. Definición formal** | Conjuntos, parámetros (con unidades y fuentes), variables de decisión | Pareja 1 |
| **3. Formulación matemática** | Función objetivo + restricciones (R1–R7) en notación LaTeX | Pareja 1 |
| **4. Análisis de complejidad** | Reducción desde SET COVER → NP-completitud, casos polinomiales | Pareja 1 |
| **5. Datos y supuestos** | Documentación de fuentes, criterios, preprocesamiento | Pareja 3 proporciona la info |
| **6. Diseño algorítmico** | Pseudocódigo, complejidad, correctitud de ILP y heurística | Pareja 2 |
| **7. Solución computacional** | Implementación, parámetros, verificación, sensibilidad | Pareja 2 |
| **8. Modelado con grafos** | Grafo A-2, MST, red de flujo, visualizaciones | Pareja 3 |
| **9. Resultados y discusión** | Mapas, tablas comparativas, implicaciones, limitaciones | Todos |
| **10. Conclusiones** | Síntesis de hallazgos, recomendaciones | Todos |
| **Referencias** | Mínimo 5 en formato APA | Pareja 1 |
| **Anexos** | Pseudocódigo extra, datos brutos, hoja de control | Todos |

**Formato:** LaTeX o Word, Times New Roman 12, interlineado 1.5, márgenes 2.5 cm, justificado.

---

## 📚 Referencias bibliográficas (mínimo 5)

1. Garey, M. R., & Johnson, D. S. (1979). *Computers and Intractability: A Guide to the Theory of NP-Completeness*. W.H. Freeman.
2. Cormen, T. H., Leiserson, C. E., Rivest, R. L., & Stein, C. (2009). *Introduction to Algorithms* (3rd ed.). MIT Press.
3. Diestel, R. (2017). *Graph Theory* (5th ed.). Springer.
4. Ahuja, R. K., Magnanti, T. L., & Orlin, J. B. (1993). *Network Flows: Theory, Algorithms, and Applications*. Prentice Hall.
5. Ministerio de Transportes y Movilidad Sostenible (2024). *Mapa de Tráfico 2024*. Gobierno de España.
6. Unión Europea (2021). *Reglamento (UE) 2021/1119 sobre infraestructura para combustibles alternativos (AFIR)*. Diario Oficial de la Unión Europea.