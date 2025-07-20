# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "requests",
# ]
# ///

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path

# Filtering parameters - adjust these to control river visibility
# Option 1: Filter by stream order (NOT recommended - major rivers have low values)
MIN_STREAM_ORDER = 8  # ORD_FLOW >= 8 keeps ~69k rivers (51% of total)
                      # ORD_FLOW >= 9 keeps ~33k rivers (25% of total)
                      # ORD_FLOW >= 7 keeps ~109k rivers (81% of total)

# Option 2: Filter by discharge (RECOMMENDED - shows major rivers properly)
USE_DISCHARGE_FILTER = True  # Set to True to use discharge instead of stream order
MIN_DISCHARGE = 0.5  # Minimum discharge in m³/s (0.5 keeps ~40k rivers)
                     # 0.1 keeps ~67k rivers, 1.0 keeps ~35k rivers, 5.0 keeps ~13k rivers

# Visual parameters
SCALE_LINE_WIDTH = True  # Scale line width based on river size
BASE_LINE_WIDTH = 0.2   # Base line width for rivers
MAX_LINE_WIDTH = 3.0    # Maximum line width for largest rivers

def main():
    print("Loading Argentina boundary...")
    
    # Load Argentina boundary from local shapefile
    countries_path = Path("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
    countries = gpd.read_file(countries_path)
    argentina = countries[countries['NAME'] == 'Argentina']
    
    print("Loading HydroRIVERS shapefile...")
    # Load South America HydroRIVERS shapefile
    hydrorivers_path = Path("data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp")
    hydrorivers = gpd.read_file(hydrorivers_path)
    
    print("Clipping rivers to Argentina...")
    # Ensure same CRS
    if hydrorivers.crs != argentina.crs:
        argentina = argentina.to_crs(hydrorivers.crs)
    
    # Clip rivers to Argentina
    argentina_rivers = gpd.clip(hydrorivers, argentina)
    
    print(f"Total rivers before filtering: {len(argentina_rivers)}")
    
    # Filter rivers by size/significance
    if USE_DISCHARGE_FILTER:
        print(f"Filtering rivers by discharge >= {MIN_DISCHARGE} m³/s...")
        argentina_rivers = argentina_rivers[argentina_rivers['DIS_AV_CMS'] >= MIN_DISCHARGE]
    else:
        print(f"Filtering rivers by stream order >= {MIN_STREAM_ORDER}...")
        argentina_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= MIN_STREAM_ORDER]
    
    print(f"Rivers after filtering: {len(argentina_rivers)}")
    
    # Stay in WGS84 for better visual proportions
    print("Using WGS84 coordinates...")
    
    print("Generating desktop background (2400px tall)...")
    
    # Calculate the actual aspect ratio of the data
    bounds = argentina_rivers.total_bounds
    data_width = bounds[2] - bounds[0]
    data_height = bounds[3] - bounds[1]
    data_aspect = data_width / data_height
    
    # Set figure dimensions
    # Use a fixed width that looks good visually
    fig_height = 24  # 2400px at 100 DPI
    fig_width = 16   # 1600px at 100 DPI
    
    print(f"Data aspect ratio: {data_aspect:.3f}")
    print(f"Creating image: 1600x2400 pixels")
    
    # Create figure with transparent background
    fig = plt.figure(figsize=(fig_width, fig_height), dpi=100, facecolor='none')
    ax = fig.add_subplot(111)
    ax.set_aspect('equal')
    
    # Plot rivers with better visibility for wallpaper
    if SCALE_LINE_WIDTH:
        # Calculate line widths based on river size
        # Use discharge or stream order for scaling
        if USE_DISCHARGE_FILTER or 'DIS_AV_CMS' in argentina_rivers.columns:
            # Normalize discharge values for line width
            discharge_values = argentina_rivers['DIS_AV_CMS'].values
            # Use log scale for better visualization
            log_discharge = np.log10(discharge_values + 1)  # +1 to avoid log(0)
            min_log = np.min(log_discharge)
            max_log = np.max(log_discharge)
            if max_log > min_log:
                normalized = (log_discharge - min_log) / (max_log - min_log)
            else:
                normalized = np.ones_like(log_discharge) * 0.5
            line_widths = BASE_LINE_WIDTH + (MAX_LINE_WIDTH - BASE_LINE_WIDTH) * normalized
        else:
            # Use stream order for line width
            order_values = argentina_rivers['ORD_FLOW'].values
            min_order = np.min(order_values)
            max_order = np.max(order_values)
            if max_order > min_order:
                normalized = (order_values - min_order) / (max_order - min_order)
            else:
                normalized = np.ones_like(order_values) * 0.5
            line_widths = BASE_LINE_WIDTH + (MAX_LINE_WIDTH - BASE_LINE_WIDTH) * normalized
        
        # Plot each river with its specific line width
        for idx, (_, river) in enumerate(argentina_rivers.iterrows()):
            geom = river.geometry
            if geom.geom_type == 'LineString':
                ax.plot(*geom.coords.xy, color='black', linewidth=line_widths[idx], alpha=1.0)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    ax.plot(*line.coords.xy, color='black', linewidth=line_widths[idx], alpha=1.0)
    else:
        # Plot all rivers with same line width
        argentina_rivers.plot(ax=ax, color='black', linewidth=BASE_LINE_WIDTH, alpha=1.0)
    
    ax.set_facecolor('none')  # Transparent background
    ax.axis('off')
    
    # Add minimal padding to preserve Argentina's natural proportions
    bounds = argentina_rivers.total_bounds
    x_range = bounds[2] - bounds[0]
    y_range = bounds[3] - bounds[1]
    
    # Use different padding for x and y to avoid squashing
    x_padding = 0.02  # Just 2% padding on x-axis
    y_padding = 0.05  # 5% padding on y-axis
    
    ax.set_xlim(bounds[0] - x_range * x_padding, bounds[2] + x_range * x_padding)
    ax.set_ylim(bounds[1] - y_range * y_padding, bounds[3] + y_range * y_padding)
    
    plt.tight_layout(pad=0.1)
    
    # Save high-res image with transparency
    plt.savefig('argentina_rivers_desktop.png', 
                facecolor='none', 
                dpi=100,
                pad_inches=0.1,
                transparent=True)
    
    print("Desktop background saved as 'argentina_rivers_desktop.png'")

if __name__ == "__main__":
    main()

