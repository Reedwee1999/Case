print("Script started")

import pandas as pd
import numpy as np
import os
from math import radians, cos, sin, sqrt, atan2

# ===== LOAD =====
rootDir = '/Volumes/IDEP/Case/Case_Study_1_Dataset'
merged_df = None

subdirs = [d for d in os.listdir(rootDir) if os.path.isdir(os.path.join(rootDir, d))]
for dir_name in subdirs:
    dir_path = os.path.join(rootDir, dir_name)
    for file in os.listdir(dir_path):
        if file.endswith('.csv'):
            file_path = os.path.join(dir_path, file)
            df = pd.read_csv(file_path)
            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.concat([merged_df, df], ignore_index=True)
            print(f"Loaded {file_path} -> current rows: {len(merged_df)}")

print(f"\n Total rows loaded: {len(merged_df)}")

# ===== CLEAN =====
print("\n Cleaning...")

# Fix data types
merged_df['started_at'] = pd.to_datetime(merged_df['started_at'])
merged_df['ended_at'] = pd.to_datetime(merged_df['ended_at'])

# Remove duplicates
merged_df.drop_duplicates(inplace=True)

# Drop rows missing end location
merged_df.dropna(subset=['end_lat', 'end_lng'], inplace=True)

# Fill missing station names
merged_df['start_station_name'].fillna('Unknown', inplace=True)
merged_df['end_station_name'].fillna('Unknown', inplace=True)

# Calculate ride duration in minutes and filter out errors (<1min or >24h)
merged_df['duration_min'] = (merged_df['ended_at'] - merged_df['started_at']).dt.total_seconds() / 60
merged_df = merged_df[(merged_df['duration_min'] >= 1) & (merged_df['duration_min'] <= 1440)]

print(f" After cleaning: {len(merged_df)} rows")

# ===== ORGANIZE =====
print("\n Organizing...")

# ---- Add Season (from month) ----
def get_season(month):
    if month in [12, 1, 2]: return 'Winter'
    elif month in [3, 4, 5]: return 'Spring'
    elif month in [6, 7, 8]: return 'Summer'
    else: return 'Fall'

merged_df['season'] = merged_df['started_at'].dt.month.apply(get_season)

# ---- Add Distance ----
def haversine_vectorized(lat1, lon1, lat2, lon2):
    """
    Vectorized Haversine distance in km.
    Works on entire columns at once.
    """
    R = 6371.0
    lat1_r = np.radians(lat1)
    lon1_r = np.radians(lon1)
    lat2_r = np.radians(lat2)
    lon2_r = np.radians(lon2)
    dlon = lon2_r - lon1_r
    dlat = lat2_r - lat1_r
    a = np.sin(dlat/2)**2 + np.cos(lat1_r) * np.cos(lat2_r) * np.sin(dlon/2)**2
    return R * 2 * np.arcsin(np.sqrt(a))

merged_df['distance_km'] = haversine_vectorized(
    merged_df['start_lat'].values,
    merged_df['start_lng'].values,
    merged_df['end_lat'].values,
    merged_df['end_lng'].values
)

print(f" New columns: {[c for c in merged_df.columns if c not in ['ride_id','rideable_type','started_at','ended_at','start_station_name','end_station_name','member_casual','duration_min']]}")
print("\n Final columns:", merged_df.columns.tolist())

# ===== SAVE AS =====
merged_df.to_csv('cleaned_cyclistic.csv', index=False)
print(" Saved to cleaned_cyclistic.csv")

print("\n All done! You can now inspect the data with:")
print("   print(merged_df.head())")
