import pandas as pd
import math

# Ruta del CSV de entrada
einput = 'data/raw/2026_04_01_R1-001_Generación.csv'
output = 'data/filtrado/subestaciones_a2.csv'

# Definición aproximada del eje A-2 en UTM 30N (Madrid – Barcelona)
a2_spine = [
    (440400, 4472600),
    (460000, 4487000),
    (520000, 4530000),
    (600000, 4568000),
    (660000, 4607000),
    (720000, 4611000),
    (780000, 4601000),
    (830000, 4612000),
    (880000, 4620000),
    (912000, 4594000),
    (925000, 4590000),
]


def point_to_segment_distance(px, py, ax, ay, bx, by):
    dx = bx - ax
    dy = by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx = ax + t * dx
    cy = ay + t * dy
    return math.hypot(px - cx, py - cy)


def distance_to_polyline(px, py, polyline):
    min_dist = float('inf')
    for i in range(len(polyline) - 1):
        ax, ay = polyline[i]
        bx, by = polyline[i + 1]
        dist = point_to_segment_distance(px, py, ax, ay, bx, by)
        if dist < min_dist:
            min_dist = dist
    return min_dist


# Leemos el CSV con pandas aplicando el separador ';' y decimal ','
df = pd.read_csv(
    einput,
    sep=';',
    decimal=',',
    encoding='utf-8-sig',
    dtype=str,
    keep_default_na=False,
)

# Convertimos coordenadas a float para calcular la distancia
def safe_float(value):
    try:
        return float(value.replace(',', '.').strip())
    except Exception:
        return None

x_col = 'Coordenada UTM X'
y_col = 'Coordenada UTM Y'
df['utm_x'] = df[x_col].apply(safe_float)
df['utm_y'] = df[y_col].apply(safe_float)

# Filtrar filas con coordenadas válidas
mask_coords = df['utm_x'].notna() & df['utm_y'].notna()
df = df[mask_coords].copy()

# Filtrar por distancia a la A-2 (umbral en metros)
umbral = 20000.0

df['dist_a2_m'] = df.apply(
    lambda row: distance_to_polyline(row['utm_x'], row['utm_y'], a2_spine),
    axis=1,
)

df_a2 = df[df['dist_a2_m'] <= umbral].copy()

# Columnas que queremos mantener
df_a2 = df_a2[
    [
        'Provincia',
        'Municipio',
        'utm_x',
        'utm_y',
        'Subestación',
        'Nivel de Tensión (kV)',
        'Capacidad disponible (MW)',
        'Identificador del Punto de Conexión',
    ]
]

# Renombrar columnas a un formato más simple
df_a2.columns = [
    'provincia',
    'municipio',
    'utm_x',
    'utm_y',
    'subestacion',
    'nivel_tension_kv',
    'capacidad_disponible_mw',
    'identificador_punto_conexion',
]

# Guardar resultado
df_a2.to_csv(output, index=False)
print('CSV creado:', output)
