# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "numpy",
# ]
# ///

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from pathlib import Path

# Filtering parameters
MIN_STREAM_ORDER = 9  # Adjust for more/less detail
SCALE_LINE_WIDTH = True
BASE_LINE_WIDTH = 0.3
MAX_LINE_WIDTH = 1.5

# Layout options
LAYOUT = "centered"  # Options: "centered", "rotated", "with_context"

def main():
    print("Loading Argentina boundary...")
    countries_path = Path("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
    countries = gpd.read_file(countries_path)
    argentina = countries[countries['NAME'] == 'Argentina']
    
    if LAYOUT == "with_context":
        # Include neighboring countries for better composition
        neighbors = countries[countries['NAME'].isin(['Chile', 'Uruguay', 'Paraguay', 'Bolivia', 'Brazil'])]
        context = gpd.GeoDataFrame(pd.concat([argentina, neighbors], ignore_index=True))
    
    print("Loading HydroRIVERS shapefile...")
    hydrorivers_path = Path("data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp")
    hydrorivers = gpd.read_file(hydrorivers_path)
    
    print("Clipping rivers to Argentina...")
    if hydrorivers.crs != argentina.crs:
        argentina = argentina.to_crs(hydrorivers.crs)
    
    argentina_rivers = gpd.clip(hydrorivers, argentina)
    
    print(f"Total rivers before filtering: {len(argentina_rivers)}")
    print(f"Filtering rivers by stream order >= {MIN_STREAM_ORDER}...")
    argentina_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= MIN_STREAM_ORDER]
    print(f"Rivers after filtering: {len(argentina_rivers)}")
    
    # Use appropriate projection
    print("Reprojecting to Argentina Albers Equal Area projection...")
    argentina_rivers = argentina_rivers.to_crs('EPSG:5346')
    argentina = argentina.to_crs('EPSG:5346')
    
    print("Generating 3840x2400 desktop background...")
    
    # Create figure with exact dimensions
    fig = plt.figure(figsize=(38.4, 24), dpi=100, facecolor='#0A0A0A')
    
    if LAYOUT == "centered":
        # Center Argentina in the wallpaper with proper aspect ratio
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        
        # Calculate centering
        bounds = argentina_rivers.total_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        
        # Center the map in the figure
        ax.set_xlim(bounds[0] - width * 0.1, bounds[2] + width * 0.1)
        ax.set_ylim(bounds[1] - height * 0.05, bounds[3] + height * 0.05)
        
    elif LAYOUT == "rotated":
        # Rotate Argentina 90 degrees for better fit
        # This would require rotating all geometries
        ax = fig.add_subplot(111)
        ax.set_aspect('equal')
        
        # Simple rotation by swapping x,y coordinates (conceptual)
        # In practice, you'd use affine transformation
        print("Rotation not implemented yet - using centered layout")
        bounds = argentina_rivers.total_bounds
        ax.set_xlim(bounds[0], bounds[2])
        ax.set_ylim(bounds[1], bounds[3])
    
    # Plot rivers
    if SCALE_LINE_WIDTH:
        # Scale line width by discharge
        discharge_values = argentina_rivers['DIS_AV_CMS'].values
        log_discharge = np.log10(discharge_values + 1)
        min_log = np.min(log_discharge)
        max_log = np.max(log_discharge)
        
        if max_log > min_log:
            normalized = (log_discharge - min_log) / (max_log - min_log)
        else:
            normalized = np.ones_like(log_discharge) * 0.5
        
        line_widths = BASE_LINE_WIDTH + (MAX_LINE_WIDTH - BASE_LINE_WIDTH) * normalized
        
        # Plot each river
        for idx, (_, river) in enumerate(argentina_rivers.iterrows()):
            geom = river.geometry
            if geom.geom_type == 'LineString':
                ax.plot(*geom.coords.xy, color='#4A90E2', linewidth=line_widths[idx], alpha=0.9)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    ax.plot(*line.coords.xy, color='#4A90E2', linewidth=line_widths[idx], alpha=0.9)
    else:
        argentina_rivers.plot(ax=ax, color='#4A90E2', linewidth=BASE_LINE_WIDTH, alpha=0.9)
    
    # Optional: Add subtle border
    argentina.boundary.plot(ax=ax, color='#2A5A8A', linewidth=0.5, alpha=0.3)
    
    ax.set_facecolor('#0A0A0A')
    ax.axis('off')
    
    # Use the full figure area
    plt.subplots_adjust(left=0, right=1, top=1, bottom=0)
    
    plt.savefig('argentina_rivers_desktop.png', 
                facecolor='#0A0A0A', 
                dpi=100,
                pad_inches=0)
    
    print("Desktop background saved as 'argentina_rivers_desktop.png'")

if __name__ == "__main__":
    main()