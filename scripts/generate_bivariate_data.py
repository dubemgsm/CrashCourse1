import geopandas as gpd
import pandas as pd
import numpy as np
import os

def main():
    # 1. Load Data
    gdf_lga = gpd.read_file('data/clean/north_east_density.geojson')
    df_schools = pd.read_csv('data/clean/north_east_schools_complete.csv')
    
    # 2. Convert schools to GeoDataFrame
    gdf_schools = gpd.GeoDataFrame(
        df_schools, 
        geometry=gpd.points_from_xy(df_schools.longitude, df_schools.latitude),
        crs="EPSG:4326"
    )
    
    # 3. Spatial Join: Count schools per LGA
    # Ensure both are in the same CRS
    gdf_lga = gdf_lga.to_crs("EPSG:4326")
    sj = gpd.sjoin(gdf_schools, gdf_lga, how="inner", predicate="within")
    school_counts = sj.groupby('NAME_2').size().reset_index(name='school_count')
    
    # 4. Merge counts back to LGA
    merged = gdf_lga.merge(school_counts, on='NAME_2', how='left').fillna(0)
    
    # 5. Calculate Supply Density (Schools per 1000 school-age children)
    # We avoid area-based density for supply to focus on the child-to-school ratio
    merged['schools_per_capita'] = (merged['school_count'] / merged['Estimated_School_Age_Pop_5_17']) * 1000
    
    # 6. Define Classes (Terciles) for Bivariate Map
    # Demand = Population Density
    # Supply = School Count (or density)
    
    def get_class(series, n=3):
        return pd.qcut(series.rank(method='first'), n, labels=[1, 2, 3]).astype(int)

    merged['demand_class'] = get_class(merged['population_density'])
    merged['supply_class'] = get_class(merged['school_count'])
    
    # 7. Bivariate ID (11, 12, 13, 21, ..., 33)
    # Format: Demand-Supply
    merged['bivariate_id'] = merged['demand_class'].astype(str) + merged['supply_class'].astype(str)
    
    # 8. Coverage Gap Index
    # Gap = Demand Class - Supply Class
    # Positive = Demand exceeds Supply
    merged['gap_index'] = merged['demand_class'] - merged['supply_class']
    
    # 9. Save to GeoJSON
    os.makedirs('data/clean', exist_ok=True)
    merged.to_file('data/clean/bay_bivariate_data.geojson', driver='GeoJSON')
    print("Bivariate data generated and saved.")

if __name__ == "__main__":
    main()
