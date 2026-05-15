import geopandas as gpd
import matplotlib.pyplot as plt

# 1. Definir la ruta del archivo
# Nota: El archivo .shp debe estar en la misma carpeta que sus archivos 
# complementarios (.dbf, .shx, .prj, etc.) para que se lea correctamente.
ruta_archivo = "estaciones_A2_filtradas.shp"

# 2. Leer el Shapefile
gdf = gpd.read_file(ruta_archivo)

# 3. Inspección básica de los datos
# Mostrar las primeras 5 filas (verás que incluye la columna 'geometry')
print("--- Primeras filas del GeoDataFrame ---")
print(gdf.head())

# Mostrar el Sistema de Referencia de Coordenadas (CRS)
print("\n--- Sistema de Coordenadas (CRS) ---")
print(gdf.crs)

# Mostrar el tipo de geometrías que contiene (Puntos, Líneas o Polígonos)
print("\n--- Tipos de geometría ---")
print(gdf.geom_type.value_counts())

# 4. Visualización rápida
# Crear una figura y dibujar las geometrías en un mapa básico
fig, ax = plt.subplots(figsize=(10, 8))

# Dibujar el GeoDataFrame
gdf.plot(ax=ax, color='lightblue', edgecolor='black', alpha=0.7)

# Añadir título y mostrar el gráfico
plt.title("Visualización de mi archivo .shp")
plt.xlabel("Longitud / X")
plt.ylabel("Latitud / Y")
plt.show()