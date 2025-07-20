# /// script
# requires-python = ">=3.8"
# dependencies = [
#     "geopandas",
#     "pandas",
# ]
# ///

import geopandas as gpd
import pandas as pd
from pathlib import Path

# Load data
countries = gpd.read_file('data/ne_10m_admin_0_countries/ne_10m_admin_0_countries.shp')
argentina = countries[countries['NAME'] == 'Argentina']
hydrorivers = gpd.read_file('data/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa_shp/HydroRIVERS_v10_sa.shp')

# Clip to Argentina
if hydrorivers.crs != argentina.crs:
    argentina = argentina.to_crs(hydrorivers.crs)
argentina_rivers = gpd.clip(hydrorivers, argentina)

# Filter by stream order
filtered_rivers = argentina_rivers[argentina_rivers['ORD_FLOW'] >= 8]

print(f"Total rivers: {len(argentina_rivers)}")
print(f"Rivers with ORD_FLOW >= 8: {len(filtered_rivers)}")

# Check the largest rivers by discharge
print("\nTop 20 rivers by discharge (DIS_AV_CMS):")
top_rivers = argentina_rivers.nlargest(20, 'DIS_AV_CMS')[['DIS_AV_CMS', 'ORD_FLOW', 'ORD_STRA', 'LENGTH_KM', 'MAIN_RIV']]
print(top_rivers)

print("\nStream order distribution:")
print(argentina_rivers['ORD_FLOW'].value_counts().sort_index())

print("\nRivers with ORD_FLOW == 10 (highest):")
highest_order = argentina_rivers[argentina_rivers['ORD_FLOW'] == 10]
print(f"Count: {len(highest_order)}")
if len(highest_order) > 0:
    print(highest_order[['DIS_AV_CMS', 'ORD_FLOW', 'LENGTH_KM']].describe())

# Check specific known major rivers by looking at high discharge
print("\nRivers with discharge > 1000 m³/s:")
major_rivers = argentina_rivers[argentina_rivers['DIS_AV_CMS'] > 1000]
print(f"Count: {len(major_rivers)}")
print(major_rivers[['DIS_AV_CMS', 'ORD_FLOW', 'ORD_STRA', 'LENGTH_KM']].sort_values('DIS_AV_CMS', ascending=False))