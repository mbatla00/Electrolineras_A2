from pathlib import Path
import unicodedata

import pandas as pd
import geopandas as gpd
from shapely.geometry import Point


# ============================================================
# Configuracion
# ============================================================
DISTANCIA_MAX_KM = 15.0
DISTANCIA_MAX_M = DISTANCIA_MAX_KM * 1000

# El script esta en src/ y data/ esta en la raiz del proyecto
ROOT_DIR = Path(__file__).resolve().parents[1]
RAW_DIR = ROOT_DIR / "data" / "raw"
FILTRADO_DIR = ROOT_DIR / "data" / "filtrado"
FILTRADO_DIR.mkdir(parents=True, exist_ok=True)

TRAMOS_A2_SHP = RAW_DIR / "250717_IMD2024_CatRCE2024.shp"

# Busca automaticamente el CSV exportado de CNMC
posibles_csv = (
    list(RAW_DIR.glob("*Demanda*Distribucion*.csv"))
    + list(RAW_DIR.glob("*Demanda*Distribución*.csv"))
)

if not posibles_csv:
    raise FileNotFoundError(
        "No encuentro el CSV de demanda en distribucion dentro de data/raw/"
    )

DEMANDA_CSV = posibles_csv[0]

SALIDA_CSV = FILTRADO_DIR / "cnmc_demanda_distribucion_a2_15km.csv"
SALIDA_RESUMEN_CSV = FILTRADO_DIR / "cnmc_demanda_distribucion_a2_15km_resumen_subestacion.csv"
SALIDA_GEOJSON = FILTRADO_DIR / "cnmc_demanda_distribucion_a2_15km.geojson"


# ============================================================
# Funciones auxiliares
# ============================================================
def normalizar_nombre_columna(nombre):
    nombre = str(nombre).strip()
    nombre = unicodedata.normalize("NFKD", nombre)
    nombre = "".join(c for c in nombre if not unicodedata.combining(c))
    nombre = nombre.lower()

    for ch in [" ", "-", "/", "(", ")", "*", "."]:
        nombre = nombre.replace(ch, "_")

    while "__" in nombre:
        nombre = nombre.replace("__", "_")

    return nombre.strip("_")


def convertir_numero(serie):
    return pd.to_numeric(
        serie.astype(str)
        .str.replace(",", ".", regex=False)
        .str.strip(),
        errors="coerce",
    )


# ============================================================
# 1. Cargar CSV de demanda en distribucion
# ============================================================
print(f"Leyendo CSV de demanda: {DEMANDA_CSV}")

demanda = pd.read_csv(DEMANDA_CSV, sep=",", encoding="utf-8-sig")
demanda.columns = [normalizar_nombre_columna(c) for c in demanda.columns]

# Coordenadas CNMC
if "coordenada_x" in demanda.columns and "coordenada_y" in demanda.columns:
    demanda["utm_x"] = convertir_numero(demanda["coordenada_x"])
    demanda["utm_y"] = convertir_numero(demanda["coordenada_y"])
elif "x" in demanda.columns and "y" in demanda.columns:
    demanda["utm_x"] = convertir_numero(demanda["x"])
    demanda["utm_y"] = convertir_numero(demanda["y"])
else:
    raise ValueError("No encuentro columnas de coordenadas en el CSV")

# Columnas numericas principales
for col in [
    "nivel_de_tension_kv",
    "capacidad_disponible_mw",
    "capacidad_ocupada_mw",
    "capacidad_admitida_y_no_evaluada_mw",
]:
    if col in demanda.columns:
        demanda[col] = convertir_numero(demanda[col])

demanda = demanda.dropna(subset=["utm_x", "utm_y"]).copy()

# Los datos de CNMC vienen en UTM ETRS89 / zona 30N
gdf_demanda = gpd.GeoDataFrame(
    demanda,
    geometry=[Point(xy) for xy in zip(demanda["utm_x"], demanda["utm_y"])],
    crs="EPSG:25830",
)

print(f"Puntos de demanda cargados: {len(gdf_demanda)}")


# ============================================================
# 2. Cargar shapefile de carreteras y filtrar A-2
# ============================================================
print(f"Leyendo shapefile de carreteras: {TRAMOS_A2_SHP}")

red = gpd.read_file(TRAMOS_A2_SHP)

if red.crs is None:
    raise ValueError("El shapefile de tramos no tiene CRS definido")

red = red.to_crs("EPSG:25830")

if "carretera" not in red.columns:
    raise ValueError("El shapefile no tiene columna 'carretera'")

a2 = red[
    red["carretera"].astype(str).str.upper().str.strip().eq("A-2")
].copy()

if a2.empty:
    raise ValueError("No se han encontrado tramos con carretera == 'A-2'")

a2 = a2.sort_values(["pk_inicio", "pk_fin"]).reset_index(drop=True)

print(f"Tramos A-2 encontrados: {len(a2)}")
print(f"PK inicial: {a2['pk_inicio'].min():.1f}")
print(f"PK final: {a2['pk_fin'].max():.1f}")

# Union geometrica de todos los tramos A-2
geom_a2 = (
    a2.geometry.union_all()
    if hasattr(a2.geometry, "union_all")
    else a2.geometry.unary_union
)


# ============================================================
# 3. Calcular distancia de cada nudo a la A-2
# ============================================================
gdf_demanda["distancia_a2_m"] = gdf_demanda.geometry.distance(geom_a2)
gdf_demanda["distancia_a2_km"] = gdf_demanda["distancia_a2_m"] / 1000

cerca_a2 = gdf_demanda[
    gdf_demanda["distancia_a2_m"] <= DISTANCIA_MAX_M
].copy()

print(f"Puntos a menos de {DISTANCIA_MAX_KM:.1f} km de la A-2: {len(cerca_a2)}")


# ============================================================
# 4. Asociar cada punto al tramo A-2 mas cercano
# ============================================================
def tramo_mas_cercano(point):
    distancias = a2.geometry.distance(point)
    idx = distancias.idxmin()
    fila = a2.loc[idx]

    return pd.Series(
        {
            "id_tramo_a2_cercano": fila.get("id_catalog", idx),
            "provincia_tramo_a2": fila.get("provincia", None),
            "pk_inicio_tramo_a2": fila.get("pk_inicio", None),
            "pk_fin_tramo_a2": fila.get("pk_fin", None),
            "pk_centro_tramo_a2": (
                float(fila.get("pk_inicio", 0)) + float(fila.get("pk_fin", 0))
            )
            / 2,
        }
    )


if not cerca_a2.empty:
    info_tramo = cerca_a2.geometry.apply(tramo_mas_cercano)
    cerca_a2 = pd.concat(
        [cerca_a2.reset_index(drop=True), info_tramo.reset_index(drop=True)],
        axis=1,
    )
else:
    print("AVISO: no hay puntos dentro de 15 km. Prueba con 20 o 30 km.")


# ============================================================
# 5. Guardar resultados
# ============================================================
sort_cols = ["distancia_a2_km"]
ascending = [True]

if "capacidad_disponible_mw" in cerca_a2.columns:
    sort_cols.append("capacidad_disponible_mw")
    ascending.append(False)

cerca_a2 = cerca_a2.sort_values(sort_cols, ascending=ascending).reset_index(drop=True)

columnas_preferidas = [
    "objectid",
    "gestor_de_red",
    "nombre_del_gestor",
    "provincia",
    "municipio",
    "subestacion",
    "nivel_de_tension_kv",
    "capacidad_disponible_mw",
    "capacidad_ocupada_mw",
    "capacidad_admitida_y_no_evaluada_mw",
    "nudo_reservado",
    "nudo_0",
    "utm_x",
    "utm_y",
    "distancia_a2_km",
    "id_tramo_a2_cercano",
    "provincia_tramo_a2",
    "pk_inicio_tramo_a2",
    "pk_fin_tramo_a2",
    "pk_centro_tramo_a2",
]

columnas_salida = [c for c in columnas_preferidas if c in cerca_a2.columns]

cerca_a2[columnas_salida].to_csv(SALIDA_CSV, index=False, encoding="utf-8-sig")
print(f"CSV filtrado guardado en: {SALIDA_CSV}")

cerca_a2.to_file(SALIDA_GEOJSON, driver="GeoJSON")
print(f"GeoJSON filtrado guardado en: {SALIDA_GEOJSON}")

# Resumen por subestacion: una fila por subestacion
if "subestacion" in cerca_a2.columns:
    agg_dict = {
        "provincia": "first",
        "municipio": "first",
        "nombre_del_gestor": "first",
        "utm_x": "first",
        "utm_y": "first",
        "distancia_a2_km": "min",
        "pk_centro_tramo_a2": "first",
    }

    if "capacidad_disponible_mw" in cerca_a2.columns:
        # Mejor max que suma, porque puede haber varias filas por tension/nudo.
        agg_dict["capacidad_disponible_mw"] = "max"

    if "nivel_de_tension_kv" in cerca_a2.columns:
        agg_dict["nivel_de_tension_kv"] = "max"

    resumen = cerca_a2.groupby("subestacion", as_index=False).agg(agg_dict)

    resumen = resumen.sort_values(
        ["distancia_a2_km", "capacidad_disponible_mw"],
        ascending=[True, False],
    )

    resumen.to_csv(SALIDA_RESUMEN_CSV, index=False, encoding="utf-8-sig")
    print(f"Resumen guardado en: {SALIDA_RESUMEN_CSV}")

print("\nPrimeros puntos filtrados:")
print(cerca_a2[columnas_salida].head(10))

if "capacidad_disponible_mw" in cerca_a2.columns:
    print("\nResumen de capacidad disponible MW:")
    print(cerca_a2["capacidad_disponible_mw"].describe())