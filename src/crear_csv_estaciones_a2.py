import pandas as pd
import geopandas as gpd

# Leer el Excel para obtener los CODESTA de la A-2
df_excel = pd.read_excel('data/raw/250717 Tráfico tramos RCE 2024.xlsx', sheet_name='Estaciones2024')
codestas_a2 = df_excel[df_excel['CARRETERA'] == 'A-2']['CODESTA'].tolist()

# Leer el shapefile de estaciones
gdf = gpd.read_file('data/raw/250717_Estaciones2024_IMD.shp')

# Filtrar las estaciones que están en la lista de CODESTA de A-2
gdf_filtered = gdf[gdf['CODESTA'].isin(codestas_a2)]

# Agregar columnas utm_x y utm_y desde la geometría
gdf_filtered['utm_x'] = gdf_filtered.geometry.x
gdf_filtered['utm_y'] = gdf_filtered.geometry.y

# Seleccionar y renombrar las columnas requeridas
df_final = gdf_filtered[['CODESTA', 'CLAVE', 'CARRETERA', 'PK', 'ID_PROVINC', 'IMD_TOTAL', 'IMD_PESADO', 'IMD_LIGERO', 'PORC_PESAD', 'utm_x', 'utm_y']]
df_final.columns = ['codesta', 'clave', 'carretera', 'pk', 'id_provincia', 'imd_total', 'imd_pesado', 'imd_ligero', 'porc_pesado', 'utm_x', 'utm_y']

# Guardar como CSV
df_final.to_csv('estaciones_a2.csv', index=False)

print("CSV creado: estaciones_a2.csv")