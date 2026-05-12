import pandas as pd
import geopandas as gpd

# Leer el shapefile de tramos
gdf = gpd.read_file('data/raw/250717_IMD2024_CatRCE2024.shp')

# Filtrar solo los tramos de la A-2
gdf_a2 = gdf[gdf['carretera'] == 'A-2'].copy()

# Calcular el centroide de cada tramo (línea)
gdf_a2['centroide'] = gdf_a2.geometry.centroid
gdf_a2['utm_x'] = gdf_a2['centroide'].x
gdf_a2['utm_y'] = gdf_a2['centroide'].y

# Seleccionar características importantes para el modelo de electrolineras
# - longitud: para determinar cobertura
# - imd_total, imd_pesado, imd_ligero: demanda de tráfico
# - pk_inicio, pk_fin: localización en la carretera
# - id_provinc: para equidad territorial
# - utm_x, utm_y: para calcular distancias
df_final = gdf_a2[['id_catalog', 'carretera', 'pk_inicio', 'pk_fin', 'longitud', 
                      'id_provinc', 'provincia', 'imd_total', 'imd_pesado', 'imd_ligero', 
                      'utm_x', 'utm_y']].copy()

# Renombrar columnas a minúsculas para coherencia
df_final.columns = ['id_tramo', 'carretera', 'pk_inicio', 'pk_fin', 'longitud',
                    'id_provincia', 'provincia', 'imd_total', 'imd_pesado', 'imd_ligero',
                    'utm_x', 'utm_y']

# Ordenar por pk_inicio para que esté ordenado a lo largo de la A-2
df_final = df_final.sort_values('pk_inicio').reset_index(drop=True)

# Guardar como CSV
df_final.to_csv('tramos_a2.csv', index=False)

print("CSV creado: tramos_a2.csv")
print(f"Total de tramos: {len(df_final)}")
print("\nPrimeros tramos:")
print(df_final.head())
