import pandas as pd
import sqlite3

# ===== CONFIGURATION =====
csv_path = '/Users/rahma/Desktop/Ew/cleaned_cyclistic.csv'
db_path = '/Volumes/IDEP/data_data.db'
chunk_size = 50000   # safe for my memory

# ===== CONNECT AND CREATE =====
conn = sqlite3.connect(db_path)
conn.execute("PRAGMA synchronous = OFF")
conn.execute("PRAGMA journal_mode = MEMORY")
conn.execute("PRAGMA cache_size = -2000000")
cursor = conn.cursor()

print("Dropping all existing tables...")
cursor.executescript("""
DROP TABLE IF EXISTS temp_rides;
DROP TABLE IF EXISTS rides;
DROP TABLE IF EXISTS coordinates;
DROP TABLE IF EXISTS stations;
""")
conn.commit()

print("Creating fresh schema...")
cursor.executescript("""
CREATE TABLE stations (
    station_id   TEXT PRIMARY KEY,
    station_name TEXT
);

CREATE TABLE coordinates (
    coordinate_id INTEGER PRIMARY KEY AUTOINCREMENT,
    ride_id       TEXT UNIQUE,
    start_lat     REAL,
    start_lng     REAL,
    end_lat       REAL,
    end_lng       REAL
);

CREATE TABLE rides (
    ride_id          TEXT PRIMARY KEY,
    rideable_type    TEXT,
    started_at       TEXT,
    ended_at         TEXT,
    duration_min     REAL,
    distance_km      REAL,
    season           TEXT,
    member_casual    TEXT,
    start_station_id TEXT,
    end_station_id   TEXT,
    coordinate_id    INTEGER
);

CREATE TABLE temp_rides (
    ride_id          TEXT,
    rideable_type    TEXT,
    started_at       TEXT,
    ended_at         TEXT,
    duration_min     REAL,
    distance_km      REAL,
    season           TEXT,
    member_casual    TEXT,
    start_station_id TEXT,
    end_station_id   TEXT,
    start_lat        REAL,
    start_lng        REAL,
    end_lat          REAL,
    end_lng          REAL
);
""")
conn.commit()

# ===== LOAD CSV IN CHUNKS =====
print("Loading CSV into temp_rides (in chunks)...")
first_chunk = True
for i, chunk in enumerate(pd.read_csv(csv_path, chunksize=chunk_size,
                                       dtype={'ride_id': str,
                                              'start_station_id': str,
                                              'end_station_id': str})):
    # Force string types
    for col in ['ride_id', 'start_station_id', 'end_station_id']:
        if col in chunk.columns:
            chunk[col] = chunk[col].astype(str)
    chunk.to_sql('temp_rides', conn, if_exists='replace' if first_chunk else 'append',
                 index=False)
    first_chunk = False
    if (i+1) % 10 == 0:
        count = cursor.execute("SELECT COUNT(*) FROM temp_rides").fetchone()[0]
        print(f"  ↳ {count:,} rows loaded so far")

# ===== BUILD COVERING INDEXES =====
print("Building covering indexes on temp_rides...")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_start_cover ON temp_rides(start_station_id, start_station_name)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_end_cover ON temp_rides(end_station_id, end_station_name)")
cursor.execute("CREATE INDEX IF NOT EXISTS idx_ride_id ON temp_rides(ride_id)")
conn.commit()

# ===== POPULATE STATIONS =====
print("Populating stations...")
cursor.execute("""
INSERT OR IGNORE INTO stations (station_id, station_name)
SELECT DISTINCT start_station_id, start_station_name
FROM temp_rides
WHERE start_station_id IS NOT NULL AND start_station_id != 'nan'
""")
cursor.execute("""
INSERT OR IGNORE INTO stations (station_id, station_name)
SELECT DISTINCT end_station_id, end_station_name
FROM temp_rides
WHERE end_station_id IS NOT NULL AND end_station_id != 'nan'
""")
stations_count = cursor.execute("SELECT COUNT(*) FROM stations").fetchone()[0]
print(f"  ↳ {stations_count} unique stations inserted")

# ===== POPULATE COORDINATES =====
print("Populating coordinates...")
cursor.execute("""
INSERT INTO coordinates (ride_id, start_lat, start_lng, end_lat, end_lng)
SELECT ride_id, start_lat, start_lng, end_lat, end_lng
FROM temp_rides
""")
coords_count = cursor.execute("SELECT COUNT(*) FROM coordinates").fetchone()[0]
print(f"  ↳ {coords_count:,} coordinate records inserted")

# ===== POPULATE RIDES =====
print("Populating rides (joining with coordinates)...")
cursor.execute("""
INSERT INTO rides (
    ride_id, rideable_type, started_at, ended_at, duration_min,
    distance_km, season, member_casual, start_station_id, end_station_id, coordinate_id
)
SELECT 
    t.ride_id, t.rideable_type, t.started_at, t.ended_at, t.duration_min,
    t.distance_km, t.season, t.member_casual, t.start_station_id, t.end_station_id,
    c.coordinate_id
FROM temp_rides t
JOIN coordinates c ON t.ride_id = c.ride_id
""")
rides_count = cursor.execute("SELECT COUNT(*) FROM rides").fetchone()[0]
print(f"  ↳ {rides_count:,} rides inserted")

# ===== CLEANUP =====
print("Dropping temp_rides...")
cursor.execute("DROP TABLE temp_rides")
conn.commit()

# ===== RESTORE SAFE SETTINGS =====
conn.execute("PRAGMA journal_mode = DELETE")
conn.execute("PRAGMA synchronous = NORMAL")
conn.close()

print("ALL TABLES FILLED SUCCESSFULLY!")
print(f"   Stations: {stations_count}")
print(f"   Coordinates: {coords_count:,}")
print(f"   Rides: {rides_count:,}")
print("   Use DB Browser for SQLite to verify.")
