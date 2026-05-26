import os
import geopandas as gpd
import pandas as pd

def main():
    # Directories
    raw_shp_path = 'data/raw/nga_education_shp/NGA_Education.shp'
    clean_dir = 'data/clean'
    os.makedirs(clean_dir, exist_ok=True)

    print(f"Loading shapefile from {raw_shp_path}...")
    # Read the shapefile
    gdf = gpd.read_file(raw_shp_path)
    
    # Filter for North East states (Adamawa, Borno, Yobe)
    # Based on previous check, codes are AD, BR, YO
    state_codes = ["AD", "BR", "YO"]
    print(f"Filtering for state codes: {state_codes}")
    gdf_filtered = gdf[gdf['state_code'].isin(state_codes)].copy()
    
    # Extract Latitude and Longitude from Geometry
    print("Extracting coordinates...")
    gdf_filtered['latitude'] = gdf_filtered.geometry.y
    gdf_filtered['longitude'] = gdf_filtered.geometry.x
    
    # Select and Rename Columns for clarity
    # no_of_stud = Population/Capacity
    # no_of_teac = Teacher count
    col_mapping = {
        'name': 'school_name',
        'state_code': 'state',
        'category': 'level',
        'management': 'ownership',
        'no_of_stud': 'student_count',
        'no_of_teac': 'teacher_count',
        'latitude': 'latitude',
        'longitude': 'longitude',
        'ward_code': 'ward_code'
    }
    
    # Filter for available columns
    available_cols = [col for col in col_mapping.keys() if col in gdf_filtered.columns]
    df_clean = gdf_filtered[available_cols].rename(columns=col_mapping)
    
    # Add a formatted 'address' column based on available info
    # Usually: School Name, State
    df_clean['address'] = df_clean['school_name'] + ", " + df_clean['state'] + " State, Nigeria"
    
    # Save to CSV
    clean_path = os.path.join(clean_dir, 'north_east_schools_complete.csv')
    df_clean.to_csv(clean_path, index=False)
    
    print(f"Successfully processed {len(df_clean)} schools.")
    print(f"Cleaned data saved to: {clean_path}")
    print(f"Sample data:\n{df_clean.head(2)}")

if __name__ == "__main__":
    main()
