import pandas as pd
import folium
from folium.plugins import HeatMapWithTime, MarkerCluster
import json
import os
import numpy as np
from math import radians, cos, sin, asin, sqrt

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def main():
    print("Loading data...")
    # Load schools
    df_schools = pd.read_csv('data/clean/north_east_schools_complete.csv')
    
    # Load conflicts - using error_bad_lines equivalent for newer pandas or just simple read
    try:
        df_conflict = pd.read_csv('data/clean/conflict_data_nga_cleaned_fully.csv', on_bad_lines='skip')
    except Exception as e:
        print(f"Error reading conflict data: {e}")
        return

    # Clean conflict data: ensure numeric lat/long and year
    df_conflict['latitude'] = pd.to_numeric(df_conflict['latitude'], errors='coerce')
    df_conflict['longitude'] = pd.to_numeric(df_conflict['longitude'], errors='coerce')
    df_conflict['year'] = pd.to_numeric(df_conflict['year'], errors='coerce')
    df_conflict = df_conflict.dropna(subset=['latitude', 'longitude', 'year'])
    df_conflict['year'] = df_conflict['year'].astype(int)

    # Filter for North East states roughly (to keep map focused)
    # Adamawa, Borno, Yobe
    ne_states = ['Borno state', 'Adamawa state', 'Yobe state']
    df_conflict_ne = df_conflict[df_conflict['adm_1'].isin(ne_states)].copy()

    # Prepare HeatMapWithTime data
    years = sorted(df_conflict_ne['year'].unique())
    heat_data = []
    for year in years:
        year_data = df_conflict_ne[df_conflict_ne['year'] == year][['latitude', 'longitude']].values.tolist()
        heat_data.append(year_data)

    print(f"Creating map with {len(years)} years of conflict data...")
    # Create Base Map
    m = folium.Map(location=[11.5, 13.0], zoom_start=7, tiles='CartoDB positron')

    # 1. Add Conflict HeatMapWithTime
    hm = HeatMapWithTime(heat_data, index=[str(y) for y in years], auto_play=False, radius=15, max_opacity=0.8)
    hm.add_to(m)

    # 2. Buffer Analysis: Recent Events (2023-2024)
    print("Performing buffer analysis for recent events...")
    recent_events = df_conflict_ne[df_conflict_ne['year'] >= 2023].copy()
    
    # Simple proximity check (optimized: only check schools near the bounding box of recent events if needed, 
    # but 10k schools vs few hundred events is okay)
    # We'll highlight schools within 10km of ANY recent event
    
    at_risk_indices = set()
    buffer_radius = 10.0 # km
    
    # For visualization, we'll create a FeatureGroup for the buffers
    buffer_group = folium.FeatureGroup(name="10km Conflict Buffers (2023-2024)", show=False)
    for idx, event in recent_events.iterrows():
        folium.Circle(
            location=[event['latitude'], event['longitude']],
            radius=buffer_radius * 1000, # meters
            color='red',
            fill=True,
            fill_opacity=0.2,
            popup=f"Conflict Event {event['year']}: {event['deaths']} deaths"
        ).add_to(buffer_group)
        
        # Check schools (subsetting to speed up)
        # Narrow down schools by rough lat/long box first
        lat_min, lat_max = event['latitude'] - 0.1, event['latitude'] + 0.1
        lon_min, lon_max = event['longitude'] - 0.1, event['longitude'] + 0.1
        
        nearby_schools = df_schools[
            (df_schools['latitude'] > lat_min) & (df_schools['latitude'] < lat_max) &
            (df_schools['longitude'] > lon_min) & (df_schools['longitude'] < lon_max)
        ]
        
        for s_idx, school in nearby_schools.iterrows():
            if haversine(event['longitude'], event['latitude'], school['longitude'], school['latitude']) <= buffer_radius:
                at_risk_indices.add(s_idx)

    buffer_group.add_to(m)

    # 3. Add Schools
    print(f"Adding {len(df_schools)} schools to map...")
    marker_cluster = MarkerCluster(name="All Schools", show=True)
    at_risk_group = folium.FeatureGroup(name="High Risk Schools (within 10km of recent conflict)", show=False)

    for idx, school in df_schools.iterrows():
        popup_text = f"School: {school['school_name']}<br>State: {school['state']}"
        
        # All schools in cluster
        folium.CircleMarker(
            location=[school['latitude'], school['longitude']],
            radius=3,
            color='blue',
            fill=True,
            popup=popup_text
        ).add_to(marker_cluster)
        
        # At risk schools in separate group
        if idx in at_risk_indices:
            folium.CircleMarker(
                location=[school['latitude'], school['longitude']],
                radius=5,
                color='darkred',
                fill=True,
                fill_color='orange',
                fill_opacity=0.8,
                popup=popup_text + "<br><b>STATUS: AT RISK</b>"
            ).add_to(at_risk_group)

    marker_cluster.add_to(m)
    at_risk_group.add_to(m)

    # Add Layer Control
    folium.LayerControl().add_to(m)

    # 4. Add Legend and Title
    legend_html = '''
    <div style="position: fixed; 
                bottom: 80px; left: 20px; width: 280px; height: auto; 
                border:2px solid grey; z-index:9999; font-size:12px;
                background-color:white;
                padding: 15px;
                border-radius: 5px;
                box-shadow: 2px 2px 5px rgba(0,0,0,0.3);
                ">
    <h3 style="margin-top:0; color:#2c3e50;">Educational Access & Conflict Risk</h3>
    <p style="margin-bottom:10px;"><b>North East Nigeria (BAY States)</b></p>
    
    <div style="margin-bottom:8px;">
        <span style="display:inline-block; width:12px; height:12px; background:blue; border-radius:50%; margin-right:8px;"></span>
        Cluster/Blue Point: School Locations
    </div>
    <div style="margin-bottom:8px;">
        <span style="display:inline-block; width:12px; height:12px; background:orange; border:1px solid darkred; border-radius:50%; margin-right:8px;"></span>
        Orange Marker: High Risk School
    </div>
    <div style="margin-bottom:8px;">
        <span style="display:inline-block; width:12px; height:12px; background:rgba(255,0,0,0.2); border:1px solid red; border-radius:50%; margin-right:8px;"></span>
        Red Circle: 10km Conflict Buffer (2023-2024)
    </div>
    
    <hr style="margin:10px 0;">
    
    <p><b>Timeline Control:</b> Use the slider at the bottom to visualize conflict event density (HeatMap) from 2004 to 2024.</p>
    
    <p style="font-size:10px; color:#7f8c8d; margin-top:15px;">
        <i>Footnote: High Risk schools are those within 10km of conflict events recorded in 2023/24. 
        Data: UCDP (Conflict) & NGA Education Baseline.</i>
    </p>
    </div>
    '''
    m.get_root().html.add_child(folium.Element(legend_html))

    # Save
    output_path = 'maps/conflict_education_analysis.html'
    os.makedirs('maps', exist_ok=True)
    m.save(output_path)
    print(f"Map saved to {output_path}")

if __name__ == "__main__":
    main()
