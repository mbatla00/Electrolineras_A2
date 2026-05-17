# Electrolineras_A2

**Asignatura:** Matemática Finita II  
**Grado:** Ingeniería de Datos e Inteligencia Artificial  
**Curso:** 2025/2026

**Corredor:** A-2 (Madrid – Zaragoza – Barcelona)

---

## 🎯 Objetivo

Diseño óptimo de una red de recarga para vehículos eléctricos en la A-2 que minimice el coste total de instalación garantizando cobertura, redundancia, equidad territorial y capacidad suficiente.

---

## 👥 Equipo

| Integrante | Pareja | Rol |
|------------|:------:|-----|
| María | 1 | Formulación y complejidad |
| Sofía | 1 | Formulación y complejidad |
| Guillén | 2 | Algoritmos |
| Álvaro | 2 | Algoritmos |
| Iván | 3 | Datos, grafos y visualización |
| Marcos | 3 | Datos, grafos y visualización |

> El reparto detallado con todas las tareas está en [`REPARTO.md`](REPARTO.md)

---

## 📂 Estructura del repositorio
```
Electrolineras_A2/
│
├── README.md
├── REPARTO.md
├── .gitignore
│
├── datos/
│   ├── 250717_IMD2024_CatRCE2024.shp
│   ├── 250717_IMD2024_CatRCE2024.dbf
│   ├── 250717_IMD2024_CatRCE2024.shx
│   ├── 250717_IMD2024_CatRCE2024.prj
│   ├── 250717_IMD2024_CatRCE2024.cpg
│   ├── 250717 Estaciones2024_IMD.shp
│   ├── 250717 Estaciones2024_IMD.dbf
│   ├── 250717 Estaciones2024_IMD.shx
│   ├── 250717 Estaciones2024_IMD.prj
│   ├── 250717 Estaciones2024_IMD.cpg
│   └── 250717 Tráfico tramos RCE 2024.xlsx
│
├── notebooks/
│   ├── 01_carga_datos.ipynb
│   ├── 02_algoritmo_exacto.ipynb
│   ├── 03_algoritmo_heuristico.ipynb
│   └── 04_visualizaciones.ipynb
│
├── src/
│   └── funciones.py
│
├── informe/
│   └── informe.pdf
│
└── outputs/
    ├── imd_A2.png
    ├── solucion_A2.png
    └── mst_A2.png
```


### ¿Qué es cada archivo de datos?

| Archivo | Descripción |
|---------|-------------|
| `250717_IMD2024_CatRCE2024.shp` | Red de Carreteras del Estado con Intensidad Media Diaria (IMD) por tramo. Geometría LineString |
| `250717 Estaciones2024_IMD.shp` | Puntos de aforo donde se mide el tráfico |
| `250717 Tráfico tramos RCE 2024.xlsx` | Datos tabulares de tráfico por tramo (IMD total, ligeros, pesados, etc.) |
| `.dbf` | Tabla de atributos del shapefile |
| `.shx` | Índice espacial del shapefile |
| `.prj` | Sistema de referencia de coordenadas (CRS) |
| `.cpg` | Codificación de caracteres |

---

## 🔧 Requisitos

```bash
pip install geopandas networkx pulp matplotlib numpy pandas openpyxl
```

## 🚀 Cómo ejecutar

1. Clonar el repositorio
2. Instalar dependencias
3. Ejecutar los notebooks en orden:
   - `01_carga_datos.ipynb` → procesa datos y genera archivos intermedios
   - `02_algoritmo_exacto.ipynb` → resuelve con ILP
   - `03_algoritmo_heuristico.ipynb` → ejecuta heurística voraz y compara
   - `04_visualizaciones.ipynb` → genera mapas y gráficos para el informe

---

## 📊 Datos

**Fuente:** Mapa de Tráfico 2024 — Ministerio de Transportes y Movilidad Sostenible

**Corredor analizado:** Autovía del Nordeste **A-2** (Madrid – Guadalajara – Zaragoza – Lleida – Barcelona)

---

## 📚 Referencias

1. Garey, M. R., & Johnson, D. S. (1979). *Computers and Intractability*
2. Cormen, T. H. et al. (2009). *Introduction to Algorithms*
3. Diestel, R. (2017). *Graph Theory*
4. Ahuja, R. K. et al. (1993). *Network Flows*
5. Ministerio de Transportes (2024). *Mapa de Tráfico 2024*
6. UE (2021). *Reglamento AFIR 2021/1119*
https://www.i-de.es/conexion-red-electrica/produccion-energia/mapa-capacidad-acceso
https://experience.arcgis.com/experience/be757f98182d49378274427240778561
