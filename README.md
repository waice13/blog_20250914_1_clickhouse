# F1 Data Analysis with ClickHouse

This project demonstrates how to ingest and analyze Formula 1 telemetry data using ClickHouse database.

## Overview

The project loads F1 race data from the 2024 season (Monaco and Silverstone Grand Prix) and provides analytical queries to gain insights into driver performance, lap times, and telemetry data.

## Prerequisites

- Docker and Docker Compose
- Python 3.13.2
- pip

## Setup

### 1. Install Python dependencies

```bash
pip install fastf1 clickhouse-connect pandas
```

### 2. Start ClickHouse

```bash
docker compose up -d
```

### 3. Test FastF1 library

```bash
python test_fastf1.py
```

### 4. Ingest data to ClickHouse

```bash
python ingest_to_clickhouse.py
```

## Data Structure

The project creates two main tables in ClickHouse:

### f1_laps
- Stores lap-by-lap data including lap times, sector times, speeds
- Contains 2,992 lap records from qualifying and race sessions

### f1_telemetry
- Stores detailed telemetry data (speed, throttle, brake, gear, DRS)
- Contains 2,446 telemetry data points from fastest laps

## Sample Queries

Check `clickhouse_queries.sql` for comprehensive analytical queries including:

- Fastest lap times by driver for each Grand Prix
- Sector time comparisons
- Top speeds analysis (Monaco vs Silverstone)
- Tire compound performance
- Team performance comparisons
- Telemetry analysis (throttle, braking zones, DRS usage)

## Running Queries

Connect to ClickHouse client:

```bash
docker exec -it clickhouse clickhouse-client
```

Then run any query from the SQL file, for example:

```sql
SELECT
    GrandPrix,
    Driver,
    min(LapTime) as FastestLap
FROM f1_laps
WHERE SessionType = 'R' AND LapTime > 0
GROUP BY GrandPrix, Driver
ORDER BY GrandPrix, FastestLap;
```

## Project Structure

```
.
├── docker-compose.yml       # ClickHouse container configuration
├── test_fastf1.py          # FastF1 library test script
├── ingest_to_clickhouse.py # Data ingestion script
├── clickhouse_queries.sql  # Analytical SQL queries
└── cache/                  # FastF1 cache directory (gitignored)
```
