import geopandas as gpd
import pandas as pd
import json
import os

def normalize_name(name):
    if not isinstance(name, str): return ""
    return name.lower().replace("-", " ").replace("/", " ").replace(" ", "").strip()

def main():
    # Load Population Data
    pop_df = pd.read_csv('data/clean/north_east_population_lga.csv')
    
    # Load GeoJSON
    gdf = gpd.read_file('data/raw/nigeria_lga.geojson')
    
    # Filter for BAY states
    states = ["Adamawa", "Borno", "Yobe"]
    gdf = gdf[gdf['NAME_1'].isin(states)].copy()
    
    # Normalize names for joining
    pop_df['lga_norm'] = pop_df['LGA'].apply(normalize_name)
    gdf['lga_norm'] = gdf['NAME_2'].apply(normalize_name)
    
    # Calculate Area in Sq Km
    # UTM Zone 33N is suitable for NE Nigeria
    gdf_projected = gdf.to_crs(epsg=32633)
    gdf['area_sqkm'] = gdf_projected.geometry.area / 10**6
    
    # Custom mapping for spelling differences
    spelling_fixes = {
        "girie": "girei",
        "mayobel": "mayobelwa",
        "teungo": "toungo",
        "askirau": "askirauba",
        "maidugur": "maiduguri",
        "borsari": "bursari",
        "tarmuwa": "tarmua"
    }
    gdf['lga_norm'] = gdf['lga_norm'].replace(spelling_fixes)
    
    # Merge
    merged = gdf.merge(pop_df, on=['lga_norm'], how='left')
    
    # Calculate Density
    merged['population_density'] = merged['Total_Population_2022_Projection'] / merged['area_sqkm']
    
    # Select final columns for GeoJSON
    # We want to keep it light
    final_gdf = merged[['NAME_1', 'NAME_2', 'Total_Population_2022_Projection', 'area_sqkm', 'population_density', 'Estimated_School_Age_Pop_5_17', 'Estimated_Out_of_School_Children', 'geometry']]
    
    # Fill NaNs if any (due to naming mismatches)
    if final_gdf['population_density'].isnull().any():
        print("Warning: Some LGAs did not match population data.")
        print(merged[merged['Total_Population_2022_Projection'].isnull()][['NAME_1', 'NAME_2']])
    
    # Save as GeoJSON for the map
    os.makedirs('data/clean', exist_ok=True)
    final_gdf.to_file('data/clean/north_east_density.geojson', driver='GeoJSON')
    print("Saved merged density GeoJSON to data/clean/north_east_density.geojson")

if __name__ == "__main__":
    main()
