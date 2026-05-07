"""
filtrar_estaciones_A2.py
========================
Limpia el shapefile de estaciones de aforo (IMD 2024) para conservar
únicamente las estaciones que pertenecen al corredor A-2 Madrid–Barcelona.

Criterios de filtrado (ambos deben cumplirse):
  1. Campo CARRETERA == 'A-2'
  2. La estación está a menos de MAX_DIST_KM km del eje central
     de la autopista A-2 (polilínea aproximada en UTM 30N).

Salida:
  - estaciones_A2_filtradas.csv   → tabla con todos los atributos + X/Y
  - estaciones_A2_filtradas.shp   → nuevo shapefile listo para SIG

Requisitos:
  pip install geopandas shapely
  (Si geopandas no está disponible, el script usa solo shapely + csv.)

Uso:
  python filtrar_estaciones_A2.py
  python filtrar_estaciones_A2.py --input ruta/al/archivo.shp --dist 3.0
"""

import os
import csv
import struct
import math
import argparse

# ---------------------------------------------------------------------------
# Parámetros por defecto
# ---------------------------------------------------------------------------
DEFAULT_INPUT  = "250717_Estaciones2024_IMD.shp"
DEFAULT_OUTPUT = "estaciones_A2_filtradas"
DEFAULT_DIST   = 5.0   # km máximo de separación lateral al eje A-2

# ---------------------------------------------------------------------------
# Eje aproximado de la A-2 (UTM ETRS89 Zona 30N)
# Puntos representativos: Madrid (Km 0) → Zaragoza → Lleida → Barcelona
# Fuente: trazado OSM / IGN aproximado; suficiente para filtro de proximidad
# ---------------------------------------------------------------------------
A2_SPINE_UTM = [
    (440400, 4472600),   # Madrid (Km 0, enlace M-30)
    (460000, 4487000),   # Km 25 – Alcalá de Henares
    (520000, 4530000),   # Km 90 – Guadalajara entorno
    (600000, 4568000),   # Km 170 – Calatayud aprox.
    (660000, 4607000),   # Km 230 – Zaragoza (centro)
    (720000, 4611000),   # Km 285 – Fraga
    (780000, 4601000),   # Km 340 – Lleida
    (830000, 4612000),   # Km 400 – Cervera
    (880000, 4620000),   # Km 450 – Martorell aprox.
    (912000, 4594000),   # Km 490 – entrada Barcelona (Llobregat)
    (925000, 4590000),   # Km 504 – Barcelona (La Bordeta / Km 0 oficial BCN)
]

# ---------------------------------------------------------------------------
# Geometría mínima sin geopandas
# ---------------------------------------------------------------------------

def point_to_segment_dist(px, py, ax, ay, bx, by):
    """Distancia (metros) de un punto P al segmento AB."""
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return math.hypot(px - ax, py - ay)
    t = ((px - ax) * dx + (py - ay) * dy) / (dx * dx + dy * dy)
    t = max(0.0, min(1.0, t))
    cx, cy = ax + t * dx, ay + t * dy
    return math.hypot(px - cx, py - cy)


def dist_to_polyline(px, py, polyline):
    """Distancia mínima (metros) de un punto a una polilínea."""
    min_d = float("inf")
    for i in range(len(polyline) - 1):
        ax, ay = polyline[i]
        bx, by = polyline[i + 1]
        d = point_to_segment_dist(px, py, ax, ay, bx, by)
        if d < min_d:
            min_d = d
    return min_d

# ---------------------------------------------------------------------------
# Lectura de .dbf
# ---------------------------------------------------------------------------

def read_dbf(path):
    """Devuelve (campos, registros) del .dbf."""
    with open(path, "rb") as f:
        header = f.read(32)
        num_records  = struct.unpack("<I", header[4:8])[0]
        header_size  = struct.unpack("<H", header[8:10])[0]
        record_size  = struct.unpack("<H", header[10:12])[0]

        fields = []
        f.seek(32)
        while True:
            fd = f.read(32)
            if not fd or fd[0] == 0x0D:
                break
            name   = fd[:11].replace(b"\x00", b"").decode("latin-1").strip()
            ftype  = chr(fd[11])
            length = fd[16]
            fields.append((name, ftype, length))

        f.seek(header_size)
        records = []
        for _ in range(num_records):
            row_data = f.read(record_size)
            if not row_data or row_data[0] == 0x2A:   # registro borrado
                continue
            row, pos = {}, 1
            for name, ftype, length in fields:
                val = row_data[pos : pos + length].decode("latin-1").strip()
                row[name] = val
                pos += length
            records.append(row)
    return fields, records

# ---------------------------------------------------------------------------
# Lectura de .shp (solo puntos, shape type 1)
# ---------------------------------------------------------------------------

def read_shp_points(path):
    """Devuelve lista de (rec_index_0based, x, y) en orden del fichero."""
    points = []
    with open(path, "rb") as f:
        f.seek(100)
        idx = 0
        while True:
            rec_header = f.read(8)
            if len(rec_header) < 8:
                break
            content_len = struct.unpack(">I", rec_header[4:8])[0]
            content     = f.read(content_len * 2)
            if len(content) < 4:
                break
            shape_type = struct.unpack("<I", content[:4])[0]
            if shape_type == 1 and len(content) >= 20:
                x = struct.unpack("<d", content[4:12])[0]
                y = struct.unpack("<d", content[12:20])[0]
                points.append((idx, x, y))
            else:
                points.append((idx, None, None))
            idx += 1
    return points

# ---------------------------------------------------------------------------
# Escritura de CSV
# ---------------------------------------------------------------------------

def write_csv(path, fields, records, coords):
    """Escribe CSV con atributos + coordenadas UTM."""
    field_names = [f[0] for f in fields] + ["UTM_X", "UTM_Y"]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=field_names)
        writer.writeheader()
        for rec, (_, x, y) in zip(records, coords):
            row = dict(rec)
            row["UTM_X"] = f"{x:.2f}" if x is not None else ""
            row["UTM_Y"] = f"{y:.2f}" if y is not None else ""
            writer.writerow(row)
    print(f"  CSV guardado: {path}")

# ---------------------------------------------------------------------------
# Escritura de .shp (puntos) + .dbf + .shx + .prj
# ---------------------------------------------------------------------------

def write_shp(base_path, fields, records, coords, prj_content=None):
    """Escribe un shapefile de puntos minimalista."""
    shp_path = base_path + ".shp"
    shx_path = base_path + ".shx"
    dbf_path = base_path + ".dbf"
    prj_path = base_path + ".prj"

    n = len(records)

    # --- .shp / .shx ---
    rec_content_len = 20   # 4 (shape type) + 8 (x) + 8 (y)
    rec_total_bytes = 8 + rec_content_len   # record header + content

    file_len_words = (100 + n * rec_total_bytes) // 2  # en palabras de 16 bit

    def shp_header(file_len_w, shape_type, x_min, y_min, x_max, y_max):
        h = struct.pack(">IIIIII", 9994, 0, 0, 0, 0, 0)
        h += struct.pack(">I", file_len_w)
        h += struct.pack("<II", 1000, shape_type)
        h += struct.pack("<dddddd", x_min, y_min, x_max, y_max, 0.0, 0.0)
        h += struct.pack("<dd", 0.0, 0.0)
        return h   # 100 bytes

    xs = [c[1] for c in coords if c[1] is not None]
    ys = [c[2] for c in coords if c[2] is not None]
    x_min, x_max = (min(xs), max(xs)) if xs else (0, 0)
    y_min, y_max = (min(ys), max(ys)) if ys else (0, 0)

    shx_len_words = (100 + n * 8) // 2

    with open(shp_path, "wb") as shp, open(shx_path, "wb") as shx:
        shp.write(shp_header(file_len_words, 1, x_min, y_min, x_max, y_max))
        shx.write(shp_header(shx_len_words,  1, x_min, y_min, x_max, y_max))

        offset = 50   # en palabras (100 bytes / 2)
        for i, ((_, x, y), rec) in enumerate(zip(coords, records)):
            rec_num_word = i + 1
            content_len_word = rec_content_len // 2

            shp.write(struct.pack(">II", rec_num_word, content_len_word))
            shp.write(struct.pack("<I", 1))   # Point
            shp.write(struct.pack("<dd", x, y))

            shx.write(struct.pack(">II", offset, content_len_word))
            offset += 4 + content_len_word   # header(4w) + content

    # --- .dbf ---
    # Calcular ancho de cada campo
    dbf_fields = fields
    field_names_out = [f[0] for f in dbf_fields]
    rec_size = 1 + sum(f[2] for f in dbf_fields)
    header_size_dbf = 32 + 32 * len(dbf_fields) + 1

    with open(dbf_path, "wb") as dbf:
        dbf.write(struct.pack("BBBB", 3, 124, 5, 7))   # version, date
        dbf.write(struct.pack("<I", n))
        dbf.write(struct.pack("<HH", header_size_dbf, rec_size))
        dbf.write(b"\x00" * 20)

        for fname, ftype, flength in dbf_fields:
            name_bytes = fname.encode("latin-1")[:10].ljust(11, b"\x00")
            dbf.write(name_bytes)
            dbf.write(ftype.encode("latin-1"))
            dbf.write(b"\x00" * 4)
            dbf.write(struct.pack("BB", flength, 0))
            dbf.write(b"\x00" * 14)

        dbf.write(b"\x0D")

        for rec in records:
            dbf.write(b" ")   # not deleted
            for fname, ftype, flength in dbf_fields:
                val = rec.get(fname, "")
                encoded = val.encode("latin-1")[:flength]
                if ftype in ("N", "F"):
                    dbf.write(encoded.rjust(flength))
                else:
                    dbf.write(encoded.ljust(flength))

        dbf.write(b"\x1A")   # EOF

    # --- .prj ---
    if prj_content:
        with open(prj_path, "w") as prj:
            prj.write(prj_content)

    print(f"  Shapefile guardado: {shp_path}")

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Filtra estaciones de la A-2 Madrid–Barcelona")
    parser.add_argument("--input",  default=DEFAULT_INPUT,  help="Ruta al .shp de entrada")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="Prefijo del fichero de salida (sin extensión)")
    parser.add_argument("--dist",   type=float, default=DEFAULT_DIST,
                        help="Distancia máxima al eje A-2 en km (por defecto: 2.0)")
    args = parser.parse_args()

    shp_in  = args.input
    dbf_in  = shp_in.replace(".shp", ".dbf")
    prj_in  = shp_in.replace(".shp", ".prj")
    out_csv = args.output + ".csv"
    out_shp = args.output   # sin extensión, write_shp añade .shp etc.

    max_dist_m = args.dist * 1000.0

    print(f"\n{'='*60}")
    print(f"  Filtrado de estaciones A-2 Madrid–Barcelona")
    print(f"{'='*60}")
    print(f"  Fichero entrada : {shp_in}")
    print(f"  Distancia máx.  : {args.dist} km ({max_dist_m:.0f} m)")

    # Leer .prj
    prj_content = None
    if os.path.exists(prj_in):
        with open(prj_in) as pf:
            prj_content = pf.read()

    # Leer datos
    print("\n[1/4] Leyendo .dbf …")
    fields, records = read_dbf(dbf_in)
    print(f"      {len(records)} registros, campos: {[f[0] for f in fields]}")

    print("[2/4] Leyendo .shp …")
    all_points = read_shp_points(shp_in)
    print(f"      {len(all_points)} puntos")

    # Filtro 1: CARRETERA == 'A-2'
    print("[3/4] Aplicando filtros …")
    mask_road = [rec["CARRETERA"] == "A-2" for rec in records]
    n_road = sum(mask_road)
    print(f"      → CARRETERA='A-2': {n_road} estaciones")

    # Filtro 2: proximidad al eje A-2
    mask_prox = []
    for (idx, x, y), is_a2 in zip(all_points, mask_road):
        if not is_a2 or x is None:
            mask_prox.append(False)
            continue
        d = dist_to_polyline(x, y, A2_SPINE_UTM)
        mask_prox.append(d <= max_dist_m)

    n_prox = sum(mask_prox)
    rejected = n_road - n_prox
    print(f"      → Dentro de {args.dist} km del eje: {n_prox} estaciones")
    if rejected > 0:
        print(f"      → Descartadas por distancia excesiva: {rejected}")
        # Mostrar cuáles se descartan para transparencia
        for rec, (_, x, y), is_a2, ok in zip(records, all_points, mask_road, mask_prox):
            if is_a2 and not ok:
                d = dist_to_polyline(x, y, A2_SPINE_UTM) / 1000
                print(f"         Descartada CODESTA={rec['CODESTA']} PK={rec['PK']} "
                      f"PROV={rec['ID_PROVINC']} dist={d:.1f} km")

    # Filtrar
    filt_records = [r for r, ok in zip(records, mask_prox) if ok]
    filt_coords  = [c for c, ok in zip(all_points, mask_prox) if ok]

    print(f"\n[4/4] Guardando resultados ({n_prox} estaciones) …")
    write_csv(out_csv, fields, filt_records, filt_coords)
    write_shp(out_shp, fields, filt_records, filt_coords, prj_content)

    # Resumen estadístico
    pks = []
    for rec in filt_records:
        try:
            pks.append(float(rec["PK"]))
        except ValueError:
            pass
    pks.sort()

    print(f"\n{'='*60}")
    print(f"  RESUMEN")
    print(f"{'='*60}")
    print(f"  Estaciones totales en el shapefile : {len(records)}")
    print(f"  Con CARRETERA='A-2'                : {n_road}")
    print(f"  Filtradas (dentro de {args.dist} km)       : {n_prox}")
    if pks:
        print(f"  PK mínimo                          : {pks[0]:.1f} km")
        print(f"  PK máximo                          : {pks[-1]:.1f} km")
        print(f"  Longitud del corredor cubierto     : {pks[-1]-pks[0]:.1f} km")

    # Desglose por provincia
    provs = {}
    for rec in filt_records:
        p = rec.get("ID_PROVINC", "?")
        provs[p] = provs.get(p, 0) + 1
    prov_names = {
        "28": "Madrid", "19": "Guadalajara", "50": "Zaragoza",
        "22": "Huesca",  "25": "Lleida",      "8":  "Barcelona",
        "08": "Barcelona"
    }
    print(f"\n  Distribución por provincia:")
    for prov_id, count in sorted(provs.items(), key=lambda x: x[0]):
        name = prov_names.get(prov_id, f"Prov.{prov_id}")
        print(f"    {name:15s} (ID {prov_id:>3}): {count} estaciones")

    print(f"\n  Archivos generados:")
    print(f"    {out_csv}")
    print(f"    {out_shp}.shp / .dbf / .shx / .prj")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    main()