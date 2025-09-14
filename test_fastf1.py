import fastf1
import pandas as pd
import os

# Create cache directory if it doesn't exist
os.makedirs('cache', exist_ok=True)

# Enable cache to speed up data loading
fastf1.Cache.enable_cache('cache')

# Load session data - 2024 Monaco Grand Prix Qualifying
session = fastf1.get_session(2024, 'Monaco', 'Q')
session.load()

# Get lap times for all drivers
laps = session.laps

# Display fastest lap for each driver
fastest_laps = laps.loc[laps.groupby('Driver')['LapTime'].idxmin()]
fastest_laps = fastest_laps[['Driver', 'Team', 'LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']]
fastest_laps = fastest_laps.sort_values('LapTime').reset_index(drop=True)

print("2024 Monaco GP Qualifying - Fastest Laps")
print("=" * 50)
print(fastest_laps.to_string())

# Get telemetry data for the fastest lap
fastest_lap = laps.pick_fastest()
telemetry = fastest_lap.get_telemetry()

print("\n\nFastest Lap Telemetry Sample (first 10 rows):")
print("=" * 50)
# Check available columns and use only those present
available_cols = [col for col in ['Time', 'Speed', 'Throttle', 'Brake', 'nGear', 'DRS'] if col in telemetry.columns]
print(telemetry[available_cols].head(10))

# Calculate some basic statistics
print("\n\nTelemetry Statistics:")
print("=" * 50)
print(f"Max Speed: {telemetry['Speed'].max():.1f} km/h")
print(f"Average Speed: {telemetry['Speed'].mean():.1f} km/h")
print(f"Max Throttle: {telemetry['Throttle'].max():.1f}%")
print(f"Average Throttle: {telemetry['Throttle'].mean():.1f}%")