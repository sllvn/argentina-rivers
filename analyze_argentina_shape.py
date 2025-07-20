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

print("Argentina in original CRS (WGS84):")
bounds_wgs84 = argentina.total_bounds
width_wgs84 = bounds_wgs84[2] - bounds_wgs84[0]
height_wgs84 = bounds_wgs84[3] - bounds_wgs84[1]
print(f"  Bounds: {bounds_wgs84}")
print(f"  Width: {width_wgs84:.2f} degrees")
print(f"  Height: {height_wgs84:.2f} degrees")
print(f"  Aspect ratio (W/H): {width_wgs84/height_wgs84:.3f}")

# Try different projections
projections = {
    'EPSG:5346': 'Argentina Albers Equal Area',
    'EPSG:22183': 'Argentina Zone 3 (Central)',
    'EPSG:3857': 'Web Mercator',
    'EPSG:32720': 'UTM Zone 20S (covers most of Argentina)',
}

print("\nTrying different projections:")
for epsg, name in projections.items():
    try:
        argentina_proj = argentina.to_crs(epsg)
        bounds = argentina_proj.total_bounds
        width = bounds[2] - bounds[0]
        height = bounds[3] - bounds[1]
        aspect = width / height
        print(f"\n{name} ({epsg}):")
        print(f"  Width: {width/1000:.0f} km")
        print(f"  Height: {height/1000:.0f} km")
        print(f"  Aspect ratio (W/H): {aspect:.3f}")
    except Exception as e:
        print(f"\n{name} ({epsg}): Failed - {e}")

# Wallpaper aspect ratio
wallpaper_aspect = 3840 / 2400  # 1.6
print(f"\nWallpaper aspect ratio: {wallpaper_aspect:.3f}")
print("\nArgentina's natural aspect ratio is much narrower than the wallpaper.")
print("Options:")
print("1. Keep Argentina centered with empty space on sides")
print("2. Rotate Argentina 90 degrees")
print("3. Include neighboring countries/ocean for context")
print("4. Create an artistic composition with multiple views")

# Create visualization of the problem
fig, axes = plt.subplots(1, 3, figsize=(15, 5))

# Original orientation
ax1 = axes[0]
argentina.plot(ax=ax1, color='lightblue', edgecolor='black')
ax1.set_title('Original Orientation')
ax1.set_aspect('equal')

# Show wallpaper frame
ax2 = axes[1]
argentina.plot(ax=ax2, color='lightblue', edgecolor='black')
ax2.set_title('In 16:10 Frame')
ax2.set_aspect('equal')
# Add frame
bounds = argentina.total_bounds
center_x = (bounds[0] + bounds[2]) / 2
center_y = (bounds[1] + bounds[3]) / 2
frame_height = bounds[3] - bounds[1]
frame_width = frame_height * wallpaper_aspect
ax2.set_xlim(center_x - frame_width/2, center_x + frame_width/2)
ax2.set_ylim(bounds[1], bounds[3])
# Draw frame
from matplotlib.patches import Rectangle
frame = Rectangle((center_x - frame_width/2, bounds[1]), frame_width, frame_height, 
                  fill=False, edgecolor='red', linewidth=2)
ax2.add_patch(frame)

# Rotated option
ax3 = axes[2]
# Note: This is just for visualization - actual rotation would need coordinate transformation
argentina.plot(ax=ax3, color='lightblue', edgecolor='black')
ax3.set_title('Potential Solutions')
ax3.set_aspect('equal')

plt.tight_layout()
plt.savefig('argentina_shape_analysis.png', dpi=150)
print("\nVisualization saved as 'argentina_shape_analysis.png'")