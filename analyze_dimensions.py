# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "geopandas",
#     "matplotlib",
#     "numpy",
#     "shapely",
# ]
# ///

import geopandas as gpd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from shapely.affinity import rotate
import matplotlib.patches as patches

def analyze_argentina_dimensions():
    """Analyze Argentina's dimensions in different projections."""
    
    print("Loading Argentina boundary...")
    countries_path = Path("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
    countries = gpd.read_file(countries_path)
    argentina = countries[countries['NAME'] == 'Argentina'].copy()
    
    # Original CRS (WGS84)
    print(f"\nOriginal CRS: {argentina.crs}")
    bounds_wgs84 = argentina.total_bounds
    print(f"Bounds in WGS84: {bounds_wgs84}")
    print(f"Width (degrees): {bounds_wgs84[2] - bounds_wgs84[0]:.2f}")
    print(f"Height (degrees): {bounds_wgs84[3] - bounds_wgs84[1]:.2f}")
    print(f"Aspect ratio (W/H): {(bounds_wgs84[2] - bounds_wgs84[0]) / (bounds_wgs84[3] - bounds_wgs84[1]):.3f}")
    
    # Albers Equal Area projection
    print("\n" + "="*50)
    print("Albers Equal Area Projection (EPSG:5346)")
    argentina_albers = argentina.to_crs('EPSG:5346')
    bounds_albers = argentina_albers.total_bounds
    width_km = (bounds_albers[2] - bounds_albers[0]) / 1000
    height_km = (bounds_albers[3] - bounds_albers[1]) / 1000
    print(f"Bounds: {bounds_albers}")
    print(f"Width: {width_km:.0f} km")
    print(f"Height: {height_km:.0f} km")
    print(f"Aspect ratio (W/H): {width_km / height_km:.3f}")
    
    # Target wallpaper dimensions
    wallpaper_width = 3840
    wallpaper_height = 2400
    wallpaper_aspect = wallpaper_width / wallpaper_height  # 1.6
    
    print(f"\nTarget wallpaper: {wallpaper_width}x{wallpaper_height} (aspect ratio: {wallpaper_aspect:.3f})")
    
    # Calculate different fitting options
    argentina_aspect = width_km / height_km
    
    print("\n" + "="*50)
    print("FITTING OPTIONS:")
    
    # Option A: Fit to height
    scale_a = wallpaper_height / height_km
    result_width_a = width_km * scale_a
    print(f"\nOption A - Fit to height:")
    print(f"  Scale factor: {scale_a:.3f}")
    print(f"  Result: {result_width_a:.0f}x{wallpaper_height} pixels")
    print(f"  Empty space on sides: {(wallpaper_width - result_width_a):.0f} pixels ({(wallpaper_width - result_width_a)/wallpaper_width*100:.1f}%)")
    
    # Option B: Fit to width
    scale_b = wallpaper_width / width_km
    result_height_b = height_km * scale_b
    print(f"\nOption B - Fit to width:")
    print(f"  Scale factor: {scale_b:.3f}")
    print(f"  Result: {wallpaper_width}x{result_height_b:.0f} pixels")
    print(f"  Cropped top/bottom: {(result_height_b - wallpaper_height):.0f} pixels ({(result_height_b - wallpaper_height)/result_height_b*100:.1f}%)")
    
    # Option C: Rotation analysis
    print(f"\nOption C - Rotation analysis:")
    # Calculate diagonal and check if rotation could help
    diagonal = np.sqrt(width_km**2 + height_km**2)
    print(f"  Argentina diagonal: {diagonal:.0f} km")
    print(f"  Current orientation: {'Portrait' if height_km > width_km else 'Landscape'}")
    
    # Find optimal rotation angle
    best_angle = 0
    best_fit = float('inf')
    
    for angle in range(-45, 46, 5):
        # Rotate the geometry
        center = argentina_albers.geometry.unary_union.centroid
        rotated = rotate(argentina_albers.geometry.unary_union, angle, origin=center)
        rotated_bounds = rotated.bounds
        rot_width = (rotated_bounds[2] - rotated_bounds[0]) / 1000
        rot_height = (rotated_bounds[3] - rotated_bounds[1]) / 1000
        rot_aspect = rot_width / rot_height
        
        # Calculate how well it fits
        aspect_diff = abs(rot_aspect - wallpaper_aspect)
        if aspect_diff < best_fit:
            best_fit = aspect_diff
            best_angle = angle
    
    print(f"  Best rotation angle: {best_angle}° (aspect ratio difference: {best_fit:.3f})")
    
    # Option D: Alternative projections
    print(f"\nOption D - Alternative projections:")
    projections = {
        'UTM Zone 19S': 'EPSG:32719',
        'Argentina TM': 'EPSG:22195',
        'South America Lambert Conformal Conic': 'EPSG:102015'
    }
    
    for name, epsg in projections.items():
        try:
            argentina_proj = argentina.to_crs(epsg)
            bounds_proj = argentina_proj.total_bounds
            width_proj = (bounds_proj[2] - bounds_proj[0]) / 1000
            height_proj = (bounds_proj[3] - bounds_proj[1]) / 1000
            aspect_proj = width_proj / height_proj
            print(f"  {name}: aspect ratio = {aspect_proj:.3f}")
        except:
            print(f"  {name}: Could not project")
    
    # Option E: With context
    print(f"\nOption E - Adding context:")
    # Load neighboring countries
    neighbors = countries[countries['NAME'].isin(['Chile', 'Brazil', 'Paraguay', 'Uruguay', 'Bolivia'])]
    all_countries = gpd.GeoDataFrame(
        pd.concat([argentina, neighbors], ignore_index=True)
    ).to_crs('EPSG:5346')
    
    bounds_context = all_countries.total_bounds
    width_context = (bounds_context[2] - bounds_context[0]) / 1000
    height_context = (bounds_context[3] - bounds_context[1]) / 1000
    aspect_context = width_context / height_context
    print(f"  With neighbors: {width_context:.0f}x{height_context:.0f} km")
    print(f"  Aspect ratio: {aspect_context:.3f}")
    
    return argentina, argentina_albers

def visualize_options(argentina_wgs84, argentina_albers):
    """Create visualizations of different wallpaper options."""
    
    # Load rivers for visualization
    hydrorivers_path = Path("data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp")
    hydrorivers = gpd.read_file(hydrorivers_path)
    
    # Ensure same CRS and clip
    if hydrorivers.crs != argentina_wgs84.crs:
        argentina_wgs84 = argentina_wgs84.to_crs(hydrorivers.crs)
    
    argentina_rivers = gpd.clip(hydrorivers, argentina_wgs84)
    argentina_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= 8]  # Filter for visibility
    argentina_rivers_albers = argentina_rivers.to_crs('EPSG:5346')
    
    # Create figure with subplots for different options
    fig = plt.figure(figsize=(20, 12))
    
    # Option A: Fit to height
    ax1 = plt.subplot(2, 3, 1)
    ax1.set_title("Option A: Fit to Height", fontsize=14)
    ax1.set_aspect('equal')
    
    # Create a rectangle representing the wallpaper
    wallpaper_rect = patches.Rectangle((0, 0), 3840, 2400, 
                                     linewidth=2, edgecolor='red', 
                                     facecolor='#0A0A0A', alpha=0.3)
    ax1.add_patch(wallpaper_rect)
    
    # Plot Argentina scaled to fit height
    bounds = argentina_albers.total_bounds
    height = bounds[3] - bounds[1]
    scale = 2400 / height
    
    argentina_rivers_albers.plot(ax=ax1, color='#4A90E2', linewidth=0.5, alpha=0.7)
    
    # Transform to pixel coordinates
    ax1.set_xlim(0, 3840)
    ax1.set_ylim(0, 2400)
    
    # Calculate centering
    width_scaled = (bounds[2] - bounds[0]) * scale
    x_offset = (3840 - width_scaled) / 2
    
    # Apply transformation
    from matplotlib.transforms import Affine2D
    trans = Affine2D().scale(scale).translate(x_offset, 0) + ax1.transData
    
    for line in ax1.get_lines():
        line.set_transform(trans)
    
    ax1.text(1920, 2300, f"Empty space: {(3840-width_scaled)/3840*100:.1f}%", 
             ha='center', color='white', fontsize=10)
    
    # Option B: Fit to width
    ax2 = plt.subplot(2, 3, 2)
    ax2.set_title("Option B: Fit to Width", fontsize=14)
    ax2.set_aspect('equal')
    
    wallpaper_rect2 = patches.Rectangle((0, 0), 3840, 2400, 
                                      linewidth=2, edgecolor='red', 
                                      facecolor='#0A0A0A', alpha=0.3)
    ax2.add_patch(wallpaper_rect2)
    
    argentina_rivers_albers.plot(ax=ax2, color='#4A90E2', linewidth=0.5, alpha=0.7)
    
    # Scale to fit width
    width = bounds[2] - bounds[0]
    scale2 = 3840 / width
    height_scaled = (bounds[3] - bounds[1]) * scale2
    y_offset = (height_scaled - 2400) / 2
    
    trans2 = Affine2D().scale(scale2).translate(0, -y_offset) + ax2.transData
    for line in ax2.get_lines():
        line.set_transform(trans2)
    
    ax2.set_xlim(0, 3840)
    ax2.set_ylim(0, 2400)
    ax2.text(1920, 2300, f"Cropped: {(height_scaled-2400)/height_scaled*100:.1f}%", 
             ha='center', color='white', fontsize=10)
    
    # Option C: Rotated
    ax3 = plt.subplot(2, 3, 3)
    ax3.set_title("Option C: Rotated 30°", fontsize=14)
    ax3.set_aspect('equal')
    
    # Rotate Argentina
    center = argentina_albers.geometry.unary_union.centroid
    argentina_rotated = argentina_albers.copy()
    argentina_rotated['geometry'] = argentina_rotated.geometry.apply(
        lambda x: rotate(x, 30, origin=center)
    )
    rivers_rotated = argentina_rivers_albers.copy()
    rivers_rotated['geometry'] = rivers_rotated.geometry.apply(
        lambda x: rotate(x, 30, origin=center)
    )
    
    wallpaper_rect3 = patches.Rectangle((0, 0), 3840, 2400, 
                                      linewidth=2, edgecolor='red', 
                                      facecolor='#0A0A0A', alpha=0.3)
    ax3.add_patch(wallpaper_rect3)
    
    rivers_rotated.plot(ax=ax3, color='#4A90E2', linewidth=0.5, alpha=0.7)
    
    # Scale rotated version
    bounds_rot = rivers_rotated.total_bounds
    width_rot = bounds_rot[2] - bounds_rot[0]
    height_rot = bounds_rot[3] - bounds_rot[1]
    
    scale3 = min(3840 / width_rot, 2400 / height_rot) * 0.9
    
    trans3 = Affine2D().scale(scale3).translate(
        1920 - (bounds_rot[0] + width_rot/2) * scale3,
        1200 - (bounds_rot[1] + height_rot/2) * scale3
    ) + ax3.transData
    
    for line in ax3.get_lines():
        line.set_transform(trans3)
    
    ax3.set_xlim(0, 3840)
    ax3.set_ylim(0, 2400)
    
    # Option E: With context
    ax4 = plt.subplot(2, 3, 4)
    ax4.set_title("Option E: With Neighboring Countries", fontsize=14)
    ax4.set_aspect('equal')
    
    # Load neighbors
    countries_path = Path("data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp")
    countries = gpd.read_file(countries_path)
    neighbors = countries[countries['NAME'].isin(['Chile', 'Brazil', 'Paraguay', 'Uruguay', 'Bolivia'])]
    neighbors_albers = neighbors.to_crs('EPSG:5346')
    
    wallpaper_rect4 = patches.Rectangle((0, 0), 3840, 2400, 
                                      linewidth=2, edgecolor='red', 
                                      facecolor='#0A0A0A', alpha=0.3)
    ax4.add_patch(wallpaper_rect4)
    
    # Plot neighbors in gray
    neighbors_albers.boundary.plot(ax=ax4, color='#333333', linewidth=1, alpha=0.5)
    argentina_rivers_albers.plot(ax=ax4, color='#4A90E2', linewidth=0.5, alpha=0.7)
    
    # Scale to fit all
    all_bounds = gpd.GeoDataFrame(
        pd.concat([argentina_albers, neighbors_albers], ignore_index=True)
    ).total_bounds
    
    width_all = all_bounds[2] - all_bounds[0]
    height_all = all_bounds[3] - all_bounds[1]
    
    scale4 = min(3840 / width_all, 2400 / height_all) * 0.9
    
    trans4 = Affine2D().scale(scale4).translate(
        1920 - (all_bounds[0] + width_all/2) * scale4,
        1200 - (all_bounds[1] + height_all/2) * scale4
    ) + ax4.transData
    
    for line in ax4.get_lines():
        line.set_transform(trans4)
    
    ax4.set_xlim(0, 3840)
    ax4.set_ylim(0, 2400)
    
    # Clean up all axes
    for ax in [ax1, ax2, ax3, ax4]:
        ax.set_facecolor('#0A0A0A')
        ax.grid(True, alpha=0.2)
        ax.set_xlabel('Width (pixels)')
        ax.set_ylabel('Height (pixels)')
    
    plt.tight_layout()
    plt.savefig('argentina_wallpaper_options.png', dpi=150, facecolor='white')
    print("\nVisualization saved as 'argentina_wallpaper_options.png'")
    
    # Create a detailed comparison image
    create_detailed_comparison(argentina_albers, argentina_rivers_albers)

def create_detailed_comparison(argentina_albers, rivers_albers):
    """Create a detailed side-by-side comparison of the best options."""
    
    fig, axes = plt.subplots(1, 3, figsize=(24, 8))
    
    # Common settings
    wallpaper_width = 3840
    wallpaper_height = 2400
    
    # Option 1: Fit to height with padding
    ax = axes[0]
    ax.set_title("Fit to Height\n(Recommended)", fontsize=16, pad=20)
    ax.set_facecolor('#0A0A0A')
    
    bounds = rivers_albers.total_bounds
    height = bounds[3] - bounds[1]
    width = bounds[2] - bounds[0]
    
    # Scale to fit height with padding
    padding = 0.1  # 10% padding
    scale = wallpaper_height / (height * (1 + 2*padding))
    
    # Center horizontally
    width_scaled = width * scale
    x_offset = (wallpaper_width - width_scaled) / 2
    y_offset = wallpaper_height * padding / (1 + 2*padding)
    
    # Plot
    for _, river in rivers_albers.iterrows():
        geom = river.geometry
        if geom.geom_type == 'LineString':
            x, y = geom.coords.xy
            x_scaled = (np.array(x) - bounds[0]) * scale + x_offset
            y_scaled = (np.array(y) - bounds[1]) * scale + y_offset
            ax.plot(x_scaled, y_scaled, color='#4A90E2', linewidth=0.8, alpha=0.9)
        elif geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                x, y = line.coords.xy
                x_scaled = (np.array(x) - bounds[0]) * scale + x_offset
                y_scaled = (np.array(y) - bounds[1]) * scale + y_offset
                ax.plot(x_scaled, y_scaled, color='#4A90E2', linewidth=0.8, alpha=0.9)
    
    ax.set_xlim(0, wallpaper_width)
    ax.set_ylim(0, wallpaper_height)
    ax.set_aspect('equal')
    ax.axis('off')
    
    # Add subtle border
    rect = patches.Rectangle((1, 1), wallpaper_width-2, wallpaper_height-2, 
                           linewidth=1, edgecolor='#333333', facecolor='none')
    ax.add_patch(rect)
    
    # Option 2: Fit to width (cropped)
    ax = axes[1]
    ax.set_title("Fit to Width\n(Cropped Top/Bottom)", fontsize=16, pad=20)
    ax.set_facecolor('#0A0A0A')
    
    # Scale to fit width
    scale2 = wallpaper_width / width
    height_scaled = height * scale2
    
    # Center vertically (crop equally from top and bottom)
    y_crop = (height_scaled - wallpaper_height) / 2
    
    for _, river in rivers_albers.iterrows():
        geom = river.geometry
        if geom.geom_type == 'LineString':
            x, y = geom.coords.xy
            x_scaled = (np.array(x) - bounds[0]) * scale2
            y_scaled = (np.array(y) - bounds[1]) * scale2 - y_crop
            
            # Only plot if within bounds
            mask = (y_scaled >= 0) & (y_scaled <= wallpaper_height)
            if np.any(mask):
                ax.plot(x_scaled[mask], y_scaled[mask], color='#4A90E2', linewidth=0.8, alpha=0.9)
        elif geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                x, y = line.coords.xy
                x_scaled = (np.array(x) - bounds[0]) * scale2
                y_scaled = (np.array(y) - bounds[1]) * scale2 - y_crop
                
                mask = (y_scaled >= 0) & (y_scaled <= wallpaper_height)
                if np.any(mask):
                    ax.plot(x_scaled[mask], y_scaled[mask], color='#4A90E2', linewidth=0.8, alpha=0.9)
    
    ax.set_xlim(0, wallpaper_width)
    ax.set_ylim(0, wallpaper_height)
    ax.set_aspect('equal')
    ax.axis('off')
    
    rect = patches.Rectangle((1, 1), wallpaper_width-2, wallpaper_height-2, 
                           linewidth=1, edgecolor='#333333', facecolor='none')
    ax.add_patch(rect)
    
    # Option 3: With ocean context
    ax = axes[2]
    ax.set_title("Extended View\n(With Ocean)", fontsize=16, pad=20)
    ax.set_facecolor('#001133')  # Ocean blue
    
    # Extend bounds to include more ocean
    ocean_extend = 0.3  # 30% extension
    extended_bounds = [
        bounds[0] - width * ocean_extend,
        bounds[1] - height * ocean_extend,
        bounds[2] + width * ocean_extend,
        bounds[3] + height * ocean_extend
    ]
    
    extended_width = extended_bounds[2] - extended_bounds[0]
    extended_height = extended_bounds[3] - extended_bounds[1]
    
    # Scale to fit
    scale3 = min(wallpaper_width / extended_width, wallpaper_height / extended_height) * 0.95
    
    # Center
    x_center = (wallpaper_width - extended_width * scale3) / 2
    y_center = (wallpaper_height - extended_height * scale3) / 2
    
    # Plot Argentina outline
    argentina_outline = argentina_albers.geometry.unary_union
    if argentina_outline.geom_type == 'Polygon':
        x, y = argentina_outline.exterior.coords.xy
        x_scaled = (np.array(x) - extended_bounds[0]) * scale3 + x_center
        y_scaled = (np.array(y) - extended_bounds[1]) * scale3 + y_center
        ax.fill(x_scaled, y_scaled, color='#0A0A0A', alpha=0.9)
    elif argentina_outline.geom_type == 'MultiPolygon':
        for poly in argentina_outline.geoms:
            x, y = poly.exterior.coords.xy
            x_scaled = (np.array(x) - extended_bounds[0]) * scale3 + x_center
            y_scaled = (np.array(y) - extended_bounds[1]) * scale3 + y_center
            ax.fill(x_scaled, y_scaled, color='#0A0A0A', alpha=0.9)
    
    # Plot rivers
    for _, river in rivers_albers.iterrows():
        geom = river.geometry
        if geom.geom_type == 'LineString':
            x, y = geom.coords.xy
            x_scaled = (np.array(x) - extended_bounds[0]) * scale3 + x_center
            y_scaled = (np.array(y) - extended_bounds[1]) * scale3 + y_center
            ax.plot(x_scaled, y_scaled, color='#4A90E2', linewidth=0.8, alpha=0.9)
        elif geom.geom_type == 'MultiLineString':
            for line in geom.geoms:
                x, y = line.coords.xy
                x_scaled = (np.array(x) - extended_bounds[0]) * scale3 + x_center
                y_scaled = (np.array(y) - extended_bounds[1]) * scale3 + y_center
                ax.plot(x_scaled, y_scaled, color='#4A90E2', linewidth=0.8, alpha=0.9)
    
    ax.set_xlim(0, wallpaper_width)
    ax.set_ylim(0, wallpaper_height)
    ax.set_aspect('equal')
    ax.axis('off')
    
    rect = patches.Rectangle((1, 1), wallpaper_width-2, wallpaper_height-2, 
                           linewidth=1, edgecolor='#333333', facecolor='none')
    ax.add_patch(rect)
    
    plt.tight_layout()
    plt.savefig('argentina_wallpaper_detailed_comparison.png', dpi=150, facecolor='white')
    print("Detailed comparison saved as 'argentina_wallpaper_detailed_comparison.png'")

if __name__ == "__main__":
    import pandas as pd
    
    print("ARGENTINA WALLPAPER DIMENSION ANALYSIS")
    print("="*50)
    
    argentina_wgs84, argentina_albers = analyze_argentina_dimensions()
    
    print("\n" + "="*50)
    print("Creating visualizations...")
    visualize_options(argentina_wgs84, argentina_albers)
    
    print("\n" + "="*50)
    print("RECOMMENDATIONS:")
    print("\n1. BEST OPTION: Fit to height with padding")
    print("   - Preserves Argentina's natural shape without distortion")
    print("   - Creates elegant negative space on sides")
    print("   - Most aesthetically pleasing for a wallpaper")
    
    print("\n2. ALTERNATIVE: Extended view with ocean")
    print("   - Provides geographic context")
    print("   - Better fills the 16:10 aspect ratio")
    print("   - Ocean blue background adds visual interest")
    
    print("\n3. NOT RECOMMENDED: Rotation")
    print("   - Argentina's natural north-south orientation is iconic")
    print("   - Rotation would be confusing and unnatural")
    
    print("\nAnalysis complete!")