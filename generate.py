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
import requests
from pathlib import Path

def main():
    print("Downloading Argentina boundary...")
    
    # Download Argentina boundary from Natural Earth
    countries_url = "https://www.naturalearthdata.com/http//www.naturalearthdata.com/download/50m/cultural/ne_50m_admin_0_countries.zip"
    countries = gpd.read_file(countries_url)
    argentina = countries[countries['NAME'] == 'Argentina']
    
    print("Loading HydroRIVERS shapefile...")
    # Update this path to your HydroRIVERS shapefile
    hydrorivers_path = input("Enter path to HydroRIVERS shapefile: ")
    hydrorivers = gpd.read_file(hydrorivers_path)
    
    print("Clipping rivers to Argentina...")
    # Ensure same CRS
    if hydrorivers.crs != argentina.crs:
        argentina = argentina.to_crs(hydrorivers.crs)
    
    # Clip rivers to Argentina
    argentina_rivers = gpd.clip(hydrorivers, argentina)
    
    print("Generating 3840x2400 desktop background...")
    # Calculate aspect ratio for 3840x2400
    fig, ax = plt.subplots(figsize=(19.2, 12), dpi=200)  # 3840x2400 at 200 DPI
    
    # Plot rivers
    argentina_rivers.plot(ax=ax, color='lightblue', linewidth=0.2, alpha=0.8)
    ax.set_facecolor('black')
    ax.axis('off')
    plt.tight_layout(pad=0)
    
    # Save high-res image
    plt.savefig('argentina_rivers_desktop.png', 
                bbox_inches='tight', 
                facecolor='black', 
                dpi=200,
                pad_inches=0)
    
    print("Desktop background saved as 'argentina_rivers_desktop.png'")

if __name__ == "__main__":
    main()

