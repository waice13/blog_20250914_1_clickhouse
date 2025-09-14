-- ClickHouse F1 Data Analysis Queries

-- 1. Fastest lap times by driver for each Grand Prix
SELECT
    GrandPrix,
    Driver,
    Team,
    min(LapTime) as FastestLap,
    avg(LapTime) as AvgLapTime
FROM f1_laps
WHERE SessionType = 'R' AND LapTime > 0
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY GrandPrix, Driver, Team
ORDER BY GrandPrix, FastestLap;

-- 2. Compare sector times between drivers
SELECT
    GrandPrix,
    Driver,
    avg(Sector1Time) as AvgS1,
    avg(Sector2Time) as AvgS2,
    avg(Sector3Time) as AvgS3,
    avg(Sector1Time + Sector2Time + Sector3Time) as TotalTime
FROM f1_laps
WHERE SessionType = 'Q' AND Sector1Time > 0
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY GrandPrix, Driver
ORDER BY GrandPrix, TotalTime;

-- 3. Top speeds achieved by each driver at Monaco vs Silverstone
SELECT
    GrandPrix,
    Driver,
    Team,
    max(SpeedI1) as MaxSpeedI1,
    max(SpeedI2) as MaxSpeedI2,
    max(SpeedFL) as MaxSpeedFL,
    max(SpeedST) as MaxSpeedST
FROM f1_laps
WHERE SpeedI1 > 0
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY GrandPrix, Driver, Team
ORDER BY GrandPrix, MaxSpeedI1 DESC;

-- 4. Tire compound performance analysis by Grand Prix
SELECT
    GrandPrix,
    Compound,
    count(*) as LapCount,
    avg(LapTime) as AvgLapTime,
    min(LapTime) as BestLapTime,
    avg(TyreLife) as AvgTyreLife
FROM f1_laps
WHERE Compound != '' AND LapTime > 0
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY GrandPrix, Compound
ORDER BY GrandPrix, AvgLapTime;

-- 5. Team performance comparison across Monaco and Silverstone
SELECT
    Team,
    count(DISTINCT Driver) as DriverCount,
    count(*) as TotalLaps,
    avg(LapTime) as AvgLapTime,
    min(LapTime) as BestLapTime,
    avg(SpeedFL) as AvgTopSpeed
FROM f1_laps
WHERE LapTime > 0
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY Team
ORDER BY AvgLapTime;

-- 6. Personal best lap distribution
SELECT
    Driver,
    Team,
    countIf(IsPersonalBest = 1) as PersonalBests,
    count(*) as TotalLaps,
    (PersonalBests / TotalLaps) * 100 as PBPercentage
FROM f1_laps
GROUP BY Driver, Team
HAVING TotalLaps > 10
ORDER BY PBPercentage DESC;

-- 7. Telemetry analysis - Maximum speeds and average throttle
SELECT
    Driver,
    GrandPrix,
    max(Speed) as MaxSpeed,
    avg(Speed) as AvgSpeed,
    avg(Throttle) as AvgThrottle,
    avg(RPM) as AvgRPM,
    countIf(DRS > 0) as DRSActivations
FROM f1_telemetry
WHERE GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY Driver, GrandPrix
ORDER BY GrandPrix, MaxSpeed DESC;

-- 8. Braking zones analysis - Monaco vs Silverstone comparison
SELECT
    Driver,
    GrandPrix,
    countIf(Brake = 1) as BrakingPoints,
    count(*) as TotalPoints,
    (BrakingPoints / TotalPoints) * 100 as BrakingPercentage
FROM f1_telemetry
WHERE GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY Driver, GrandPrix
ORDER BY GrandPrix, BrakingPercentage DESC;

-- 9. Gear usage distribution
SELECT
    Driver,
    nGear,
    count(*) as UsageCount,
    count(*) * 100.0 / sum(count(*)) OVER (PARTITION BY Driver) as UsagePercentage
FROM f1_telemetry
WHERE nGear > 0
GROUP BY Driver, nGear
ORDER BY Driver, nGear;

-- 10. Session comparison - Qualifying vs Race pace
SELECT
    Driver,
    Team,
    avgIf(LapTime, SessionType = 'Q') as QualifyingPace,
    avgIf(LapTime, SessionType = 'R') as RacePace,
    RacePace - QualifyingPace as PaceDifference
FROM f1_laps
WHERE LapTime > 0 AND LapTime < 200
GROUP BY Driver, Team
HAVING QualifyingPace > 0 AND RacePace > 0
ORDER BY PaceDifference;

-- 11. Fastest sectors across all drivers in Qualifying
SELECT
    GrandPrix,
    argMin(Driver, Sector1Time) as FastestS1Driver,
    min(Sector1Time) as FastestS1Time,
    argMin(Driver, Sector2Time) as FastestS2Driver,
    min(Sector2Time) as FastestS2Time,
    argMin(Driver, Sector3Time) as FastestS3Driver,
    min(Sector3Time) as FastestS3Time
FROM f1_laps
WHERE Sector1Time > 0 AND SessionType = 'Q'
    AND GrandPrix IN ('Monaco', 'Silverstone')
GROUP BY GrandPrix;

-- 12. Lap time evolution during race (first 20 laps)
SELECT
    GrandPrix,
    LapNumber,
    avg(LapTime) as AvgLapTime,
    min(LapTime) as FastestLapTime,
    max(LapTime) as SlowestLapTime
FROM f1_laps
WHERE SessionType = 'R' AND LapTime > 0 AND LapTime < 200
    AND GrandPrix IN ('Monaco', 'Silverstone')
    AND LapNumber <= 20
GROUP BY GrandPrix, LapNumber
ORDER BY GrandPrix, LapNumber;