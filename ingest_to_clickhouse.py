import fastf1
import pandas as pd
import clickhouse_connect
import os
from datetime import datetime

# Create cache directory if it doesn't exist
os.makedirs('cache', exist_ok=True)

# Enable cache to speed up data loading
fastf1.Cache.enable_cache('cache')

# Connect to ClickHouse
client = clickhouse_connect.get_client(
    host='localhost',
    port=8123
)

# Load multiple sessions for more data
sessions_to_load = [
    (2024, 'Monaco', 'Q'),
    (2024, 'Monaco', 'R'),
    (2024, 'Silverstone', 'Q'),
    (2024, 'Silverstone', 'R'),
]

print("Loading F1 sessions data...")
all_laps = []
all_telemetry = []

for year, gp, session_type in sessions_to_load:
    print(f"Loading {year} {gp} - {session_type}")
    try:
        session = fastf1.get_session(year, gp, session_type)
        session.load()

        # Get lap data
        laps = session.laps
        if not laps.empty:
            laps_df = laps[['Driver', 'Team', 'LapNumber', 'LapTime', 'Sector1Time',
                           'Sector2Time', 'Sector3Time', 'SpeedI1', 'SpeedI2', 'SpeedFL',
                           'SpeedST', 'IsPersonalBest', 'Compound', 'TyreLife']].copy()
            laps_df['GrandPrix'] = gp
            laps_df['Year'] = year
            laps_df['SessionType'] = session_type
            laps_df['SessionDate'] = session.date

            # Convert timedelta to seconds
            for col in ['LapTime', 'Sector1Time', 'Sector2Time', 'Sector3Time']:
                if col in laps_df.columns:
                    laps_df[col] = laps_df[col].dt.total_seconds()

            all_laps.append(laps_df)

        # Get telemetry for fastest lap
        if not laps.empty:
            fastest_lap = laps.pick_fastest()
            telemetry = fastest_lap.get_telemetry()

            if not telemetry.empty:
                telemetry_df = telemetry[['Time', 'Speed', 'Throttle', 'Brake',
                                         'nGear', 'DRS', 'RPM']].copy()
                telemetry_df['Driver'] = fastest_lap['Driver']
                telemetry_df['GrandPrix'] = gp
                telemetry_df['Year'] = year
                telemetry_df['SessionType'] = session_type
                telemetry_df['LapNumber'] = fastest_lap['LapNumber']

                # Convert Time to seconds
                telemetry_df['Time'] = telemetry_df['Time'].dt.total_seconds()

                all_telemetry.append(telemetry_df)

    except Exception as e:
        print(f"Error loading {year} {gp} - {session_type}: {e}")
        continue

# Combine all data
laps_data = pd.concat(all_laps, ignore_index=True) if all_laps else pd.DataFrame()
telemetry_data = pd.concat(all_telemetry, ignore_index=True) if all_telemetry else pd.DataFrame()

print(f"\nCollected {len(laps_data)} lap records and {len(telemetry_data)} telemetry records")

# Create tables in ClickHouse
print("\nCreating ClickHouse tables...")

# Drop existing tables
client.command("DROP TABLE IF EXISTS f1_laps")
client.command("DROP TABLE IF EXISTS f1_telemetry")

# Create laps table
client.command("""
CREATE TABLE f1_laps (
    Year UInt16,
    GrandPrix String,
    SessionType String,
    SessionDate DateTime,
    Driver String,
    Team String,
    LapNumber UInt8,
    LapTime Float32,
    Sector1Time Float32,
    Sector2Time Float32,
    Sector3Time Float32,
    SpeedI1 Float32,
    SpeedI2 Float32,
    SpeedFL Float32,
    SpeedST Float32,
    IsPersonalBest Bool,
    Compound String,
    TyreLife UInt8
) ENGINE = MergeTree()
ORDER BY (Year, GrandPrix, SessionType, Driver, LapNumber)
""")

# Create telemetry table
client.command("""
CREATE TABLE f1_telemetry (
    Year UInt16,
    GrandPrix String,
    SessionType String,
    Driver String,
    LapNumber UInt8,
    Time Float32,
    Speed Float32,
    Throttle Float32,
    Brake Bool,
    nGear UInt8,
    DRS UInt8,
    RPM Float32
) ENGINE = MergeTree()
ORDER BY (Year, GrandPrix, SessionType, Driver, LapNumber, Time)
""")

# Insert data
if not laps_data.empty:
    print("\nInserting lap data into ClickHouse...")
    # Clean data before insertion
    laps_data = laps_data.fillna(0)
    laps_data['SessionDate'] = pd.to_datetime(laps_data['SessionDate'])

    client.insert_df('f1_laps', laps_data)
    print(f"Inserted {len(laps_data)} lap records")

if not telemetry_data.empty:
    print("\nInserting telemetry data into ClickHouse...")
    # Clean data before insertion
    telemetry_data = telemetry_data.fillna(0)
    telemetry_data['Brake'] = telemetry_data['Brake'].astype(bool)

    client.insert_df('f1_telemetry', telemetry_data)
    print(f"Inserted {len(telemetry_data)} telemetry records")

# Verify data
lap_count = client.query("SELECT count(*) FROM f1_laps").result_rows[0][0]
telemetry_count = client.query("SELECT count(*) FROM f1_telemetry").result_rows[0][0]
print(f"Total laps in database: {lap_count}")
print(f"Total telemetry records in database: {telemetry_count}")