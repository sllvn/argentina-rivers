# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "geopandas",
#     "matplotlib",
# ]
# ///

import geopandas as gpd
import matplotlib.pyplot as plt
from pathlib import Path

# Load Argentina
countries = gpd.read_file('data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
argentina = countries[countries['NAME'] == 'Argentina']

# Load rivers
hydrorivers = gpd.read_file('data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp')
argentina_rivers = gpd.clip(hydrorivers, argentina)
argentina_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= 9]

print("Original CRS (WGS84):")
print(f"  Argentina CRS: {argentina.crs}")
print(f"  Rivers CRS: {argentina_rivers.crs}")
bounds = argentina.total_bounds
print(f"  Bounds: {bounds}")
print(f"  Width: {bounds[2] - bounds[0]:.2f} degrees")
print(f"  Height: {bounds[3] - bounds[1]:.2f} degrees")
print(f"  Aspect ratio: {(bounds[2] - bounds[0])/(bounds[3] - bounds[1]):.3f}")

# Try different projections
projections = {
    'EPSG:4326': 'WGS84 (unprojected)',
    'EPSG:5346': 'Argentina Albers Equal Area',
    'EPSG:3857': 'Web Mercator',
    'EPSG:32720': 'UTM Zone 20S',
    '+proj=lcc +lat_1=-30 +lat_2=-40 +lat_0=-35 +lon_0=-60 +x_0=0 +y_0=0 +datum=WGS84 +units=m +no_defs': 'Lambert Conformal Conic (custom)',
}

# Create comparison figure
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()

for idx, (proj_code, proj_name) in enumerate(projections.items()):
    if idx >= len(axes):
        break
        
    ax = axes[idx]
    
    try:
        # Reproject
        argentina_proj = argentina.to_crs(proj_code)
        rivers_proj = argentina_rivers.to_crs(proj_code)
        
        # Plot
        rivers_proj.plot(ax=ax, color='lightblue', linewidth=0.5)
        argentina_proj.boundary.plot(ax=ax, color='black', linewidth=1)
        
        # Calculate aspect ratio
        bounds = argentina_proj.total_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        aspect = width / height
        
        ax.set_title(f'{proj_name}\nAspect: {aspect:.3f}')
        ax.set_aspect('equal')
        ax.axis('off')
        
        print(f"\n{proj_name}:")
        print(f"  Width: {width/1000:.0f} km" if 'degree' not in str(argentina_proj.crs.axis_info[0].unit_name) else f"  Width: {width:.2f} degrees")
        print(f"  Height: {height/1000:.0f} km" if 'degree' not in str(argentina_proj.crs.axis_info[0].unit_name) else f"  Height: {height:.2f} degrees")
        print(f"  Aspect ratio: {aspect:.3f}")
        
    except Exception as e:
        print(f"\n{proj_name}: Error - {e}")
        ax.text(0.5, 0.5, f'Error:\n{str(e)[:50]}...', ha='center', va='center', transform=ax.transAxes)
        ax.axis('off')

# Remove empty subplot
if len(projections) < len(axes):
    fig.delaxes(axes[-1])

plt.tight_layout()
plt.savefig('projection_comparison.png', dpi=150, facecolor='white')
print("\nComparison saved as 'projection_comparison.png'")