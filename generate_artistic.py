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
from pathlib import Path
from matplotlib.patches import Rectangle

# Filtering parameters
MIN_STREAM_ORDER = 8  # Show more rivers for artistic effect
SCALE_LINE_WIDTH = True
BASE_LINE_WIDTH = 0.2
MAX_LINE_WIDTH = 2.0

def main():
    print("Loading data...")
    countries = gpd.read_file('data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
    argentina = countries[countries['NAME'] == 'Argentina']
    
    hydrorivers = gpd.read_file('data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp')
    
    # Clip to Argentina
    if hydrorivers.crs != argentina.crs:
        argentina = argentina.to_crs(hydrorivers.crs)
    
    argentina_rivers = gpd.clip(hydrorivers, argentina)
    argentina_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= MIN_STREAM_ORDER]
    
    # Reproject
    argentina_rivers = argentina_rivers.to_crs('EPSG:5346')
    argentina = argentina.to_crs('EPSG:5346')
    
    print(f"Filtered to {len(argentina_rivers)} rivers")
    
    # Create artistic composition
    fig = plt.figure(figsize=(38.4, 24), dpi=100, facecolor='#050510')
    
    # Option 1: Three panel view - full country + two detailed regions
    # Left panel: Full Argentina
    ax1 = plt.subplot2grid((1, 3), (0, 0), rowspan=1, colspan=1)
    ax1.set_aspect('equal')
    
    # Middle panel: Northern detail (around Paraná River)
    ax2 = plt.subplot2grid((1, 3), (0, 1), rowspan=1, colspan=1)
    ax2.set_aspect('equal')
    
    # Right panel: Southern detail (Patagonia)
    ax3 = plt.subplot2grid((1, 3), (0, 2), rowspan=1, colspan=1)
    ax3.set_aspect('equal')
    
    # Calculate line widths
    discharge_values = argentina_rivers['DIS_AV_CMS'].values
    log_discharge = np.log10(discharge_values + 0.1)
    min_log, max_log = np.min(log_discharge), np.max(log_discharge)
    normalized = (log_discharge - min_log) / (max_log - min_log) if max_log > min_log else np.ones_like(log_discharge) * 0.5
    line_widths = BASE_LINE_WIDTH + (MAX_LINE_WIDTH - BASE_LINE_WIDTH) * normalized
    
    # Plot function
    def plot_rivers(ax, rivers_gdf, line_widths, alpha=0.8):
        for idx, (_, river) in enumerate(rivers_gdf.iterrows()):
            geom = river.geometry
            lw = line_widths[idx]
            # Use gradient of blues based on size
            color = plt.cm.Blues(0.5 + normalized[idx] * 0.5)
            
            if geom.geom_type == 'LineString':
                ax.plot(*geom.coords.xy, color=color, linewidth=lw, alpha=alpha)
            elif geom.geom_type == 'MultiLineString':
                for line in geom.geoms:
                    ax.plot(*line.coords.xy, color=color, linewidth=lw, alpha=alpha)
    
    # Full country view
    plot_rivers(ax1, argentina_rivers, line_widths)
    argentina.boundary.plot(ax=ax1, color='#1A3A5A', linewidth=1, alpha=0.5)
    bounds = argentina_rivers.total_bounds
    padding = 0.1
    ax1.set_xlim(bounds[0] - (bounds[2]-bounds[0])*padding, bounds[2] + (bounds[2]-bounds[0])*padding)
    ax1.set_ylim(bounds[1] - (bounds[3]-bounds[1])*padding, bounds[3] + (bounds[3]-bounds[1])*padding)
    
    # Northern detail - focus on Paraná River system
    north_bounds = [-4e6, 4e6, -2e6, 7e6]  # Approximate bounds in EPSG:5346
    ax2.set_xlim(north_bounds[0], north_bounds[2])
    ax2.set_ylim(north_bounds[1], north_bounds[3])
    plot_rivers(ax2, argentina_rivers, line_widths * 1.5, alpha=0.9)
    
    # Southern detail - Patagonia
    south_bounds = [-4e6, -2e6, -2e6, 2e6]  # Approximate bounds in EPSG:5346
    ax3.set_xlim(south_bounds[0], south_bounds[2])
    ax3.set_ylim(south_bounds[1], south_bounds[3])
    plot_rivers(ax3, argentina_rivers, line_widths * 1.5, alpha=0.9)
    
    # Style all axes
    for ax in [ax1, ax2, ax3]:
        ax.set_facecolor('#050510')
        ax.axis('off')
    
    # Add subtle labels
    ax1.text(0.5, 0.02, 'ARGENTINA', transform=ax1.transAxes, 
             fontsize=20, color='#4A90E2', alpha=0.5, ha='center', 
             fontfamily='sans-serif', weight='light')
    
    plt.subplots_adjust(left=0.02, right=0.98, top=0.98, bottom=0.02, wspace=0.05)
    
    plt.savefig('argentina_rivers_artistic.png', 
                facecolor='#050510', 
                dpi=100,
                pad_inches=0)
    
    print("Artistic wallpaper saved as 'argentina_rivers_artistic.png'")

if __name__ == "__main__":
    main()