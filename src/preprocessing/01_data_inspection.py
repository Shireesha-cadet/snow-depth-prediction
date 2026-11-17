
import duckdb

# ==========================================================
# SNOW DEPTH PREDICTION
# STEP 1: DATASET INSPECTION
# ==========================================================

DATASET_PATH = "F:/final_dataset_with_modis_fixed._wyomingcsv.csv"

con = duckdb.connect()

con.execute("SET threads = 6")

print("\n" + "=" * 65)
print("SNOW DEPTH DATASET INSPECTION")
print("=" * 65)

# ----------------------------------------------------------
# 1. DATASET DIMENSIONS
# ----------------------------------------------------------

print("\n1. DATASET DIMENSIONS")

rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchone()[0]

columns = len(con.execute(f"""
    DESCRIBE SELECT *
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchall())

print("Total rows:", f"{rows:,}")
print("Total columns:", columns)

# ----------------------------------------------------------
# 2. COLUMN NAMES AND DATA TYPES
# ----------------------------------------------------------

print("\n2. COLUMN NAMES AND DATA TYPES")

column_info = con.execute(f"""
    DESCRIBE SELECT *
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(column_info.to_string(index=False))

# ----------------------------------------------------------
# 3. MISSING VALUE ANALYSIS
# ----------------------------------------------------------

print("\n3. MISSING VALUE ANALYSIS")

missing_query = f"""
    SELECT
        {' , '.join([
            f'COUNT(*) FILTER (WHERE "{col}" IS NULL) AS "{col}"'
            for col in column_info["column_name"]
        ])}
    FROM read_csv_auto('{DATASET_PATH}')
"""

missing_values = con.execute(missing_query).fetchdf().T

missing_values.columns = ["Missing_Count"]
missing_values["Missing_Percentage"] = (
    missing_values["Missing_Count"] / rows
) * 100

print(missing_values.to_string())

# ----------------------------------------------------------
# 4. EXACT DUPLICATE ROW ANALYSIS
# ----------------------------------------------------------

print("\n4. EXACT DUPLICATE ROW ANALYSIS")

distinct_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM (
        SELECT DISTINCT *
        FROM read_csv_auto('{DATASET_PATH}')
    )
""").fetchone()[0]

duplicate_rows = rows - distinct_rows

print("Total rows:", f"{rows:,}")
print("Unique rows:", f"{distinct_rows:,}")
print("Exact duplicate rows:", f"{duplicate_rows:,}")

# ----------------------------------------------------------
# 5. DUPLICATE STATION-DATE ANALYSIS
# ----------------------------------------------------------

print("\n5. DUPLICATE STATION-DATE ANALYSIS")

duplicate_station_dates = con.execute(f"""
    SELECT COUNT(*)
    FROM (
        SELECT Station_ID, Date
        FROM read_csv_auto('{DATASET_PATH}')
        GROUP BY Station_ID, Date
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print(
    "Duplicate Station_ID-Date combinations:",
    f"{duplicate_station_dates:,}"
)

# ----------------------------------------------------------
# 6. SNOW DEPTH STATISTICS
# ----------------------------------------------------------

print("\n6. SNOW DEPTH STATISTICS (mm)")

snow_stats = con.execute(f"""
    SELECT
        COUNT(SnowDepth) AS total_records,
        MIN(SnowDepth) AS minimum,
        MAX(SnowDepth) AS maximum,
        AVG(SnowDepth) AS mean,
        MEDIAN(SnowDepth) AS median,
        QUANTILE_CONT(SnowDepth, 0.25) AS Q1,
        QUANTILE_CONT(SnowDepth, 0.75) AS Q3,
        QUANTILE_CONT(SnowDepth, 0.90) AS P90,
        QUANTILE_CONT(SnowDepth, 0.95) AS P95,
        QUANTILE_CONT(SnowDepth, 0.99) AS P99
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(snow_stats.to_string(index=False))

# ----------------------------------------------------------
# 7. EXTREME SNOW DEPTH ANALYSIS
# ----------------------------------------------------------

print("\n7. EXTREME SNOW DEPTH ANALYSIS")

extreme_stats = con.execute(f"""
    SELECT
        COUNT(*) FILTER (WHERE SnowDepth > 2000) AS above_2000,
        COUNT(*) FILTER (WHERE SnowDepth > 5000) AS above_5000,
        COUNT(*) FILTER (WHERE SnowDepth > 10000) AS above_10000,
        COUNT(*) FILTER (WHERE SnowDepth > 20000) AS above_20000,
        COUNT(*) FILTER (WHERE SnowDepth > 50000) AS above_50000,
        COUNT(*) FILTER (WHERE SnowDepth <= 0) AS non_positive
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(extreme_stats.to_string(index=False))

# ----------------------------------------------------------
# 8. STATION AND GEOGRAPHICAL COVERAGE
# ----------------------------------------------------------

print("\n8. STATION AND GEOGRAPHICAL COVERAGE")

geo_stats = con.execute(f"""
    SELECT
        COUNT(DISTINCT Station_ID) AS unique_stations,
        MIN(Latitude) AS minimum_latitude,
        MAX(Latitude) AS maximum_latitude,
        MIN(Longitude) AS minimum_longitude,
        MAX(Longitude) AS maximum_longitude
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(geo_stats.to_string(index=False))

# ----------------------------------------------------------
# 9. DATE COVERAGE
# ----------------------------------------------------------

print("\n9. DATE COVERAGE")

date_stats = con.execute(f"""
    SELECT
        MIN(Date) AS first_date,
        MAX(Date) AS last_date,
        COUNT(DISTINCT Date) AS unique_dates
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(date_stats.to_string(index=False))

# ----------------------------------------------------------
# 10. COMPLETION
# ----------------------------------------------------------

con.close()

print("\n" + "=" * 65)
print("DATASET INSPECTION COMPLETED SUCCESSFULLY")
print("=" * 65)
