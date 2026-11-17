import duckdb
import os

# ==========================================================
# SNOW DEPTH PREDICTION
# STEP 3: DATA QUALITY ANALYSIS
# ==========================================================

DATASET_PATH = "F:/final_snow_depth_dataset_cleaned_reproduced.csv"

OUTPUT_DIR = "F:/snow_data_quality_reports"

os.makedirs(OUTPUT_DIR, exist_ok=True)

con = duckdb.connect()
con.execute("SET threads = 6")

print("=" * 65)
print("SNOW DEPTH DATA QUALITY ANALYSIS")
print("=" * 65)

# ----------------------------------------------------------
# 1. Dataset overview
# ----------------------------------------------------------

print("\n1. DATASET OVERVIEW")

total_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchone()[0]

print("Total records:", f"{total_rows:,}")

# ----------------------------------------------------------
# 2. Missing value analysis
# ----------------------------------------------------------

print("\n2. MISSING VALUE ANALYSIS")

columns = con.execute(f"""
    DESCRIBE SELECT *
    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()["column_name"].tolist()

missing_query = f"""
    SELECT
        {', '.join(
            f'COUNT(*) FILTER (WHERE "{col}" IS NULL) AS "{col}"'
            for col in columns
        )}
    FROM read_csv_auto('{DATASET_PATH}')
"""

missing = con.execute(missing_query).fetchdf().T

missing.columns = ["Missing_Count"]

missing["Missing_Percentage"] = (
    missing["Missing_Count"] / total_rows
) * 100

missing = missing.sort_values(
    "Missing_Percentage",
    ascending=False
)

print(missing.to_string())

missing.to_csv(
    os.path.join(OUTPUT_DIR, "missing_values.csv")
)

# ----------------------------------------------------------
# 3. SnowDepth statistical analysis
# ----------------------------------------------------------

print("\n3. SNOW DEPTH DISTRIBUTION")

stats = con.execute(f"""
    SELECT
        COUNT(*) AS records,
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

print(stats.to_string(index=False))

stats.to_csv(
    os.path.join(OUTPUT_DIR, "snow_depth_statistics.csv"),
    index=False
)

# ----------------------------------------------------------
# 4. Extreme observation analysis
# ----------------------------------------------------------

print("\n4. EXTREME SNOW DEPTH OBSERVATIONS")

extreme = con.execute(f"""
    SELECT
        COUNT(*) FILTER (
            WHERE SnowDepth > 2000
        ) AS above_2000,

        COUNT(*) FILTER (
            WHERE SnowDepth > 5000
        ) AS above_5000,

        COUNT(*) FILTER (
            WHERE SnowDepth > 10000
        ) AS above_10000,

        COUNT(*) FILTER (
            WHERE SnowDepth > 20000
        ) AS above_20000,

        COUNT(*) FILTER (
            WHERE SnowDepth > 50000
        ) AS above_50000

    FROM read_csv_auto('{DATASET_PATH}')
""").fetchdf()

print(extreme.to_string(index=False))

extreme.to_csv(
    os.path.join(OUTPUT_DIR, "extreme_observation_counts.csv"),
    index=False
)

# ----------------------------------------------------------
# 5. IQR-based statistical screening
# ----------------------------------------------------------

print("\n5. IQR-BASED OUTLIER SCREENING")

iqr_results = con.execute(f"""
    WITH quartiles AS (
        SELECT
            QUANTILE_CONT(SnowDepth, 0.25) AS Q1,
            QUANTILE_CONT(SnowDepth, 0.75) AS Q3
        FROM read_csv_auto('{DATASET_PATH}')
    )

    SELECT
        Q1,
        Q3,
        Q3 - Q1 AS IQR,
        Q3 + 1.5 * (Q3 - Q1) AS upper_fence,
        COUNT(*) FILTER (
            WHERE SnowDepth > Q3 + 1.5 * (Q3 - Q1)
        ) AS potential_outliers

    FROM read_csv_auto('{DATASET_PATH}'), quartiles
    GROUP BY Q1, Q3
""").fetchdf()

print(iqr_results.to_string(index=False))

iqr_results.to_csv(
    os.path.join(OUTPUT_DIR, "iqr_outlier_analysis.csv"),
    index=False
)

# ----------------------------------------------------------
# 6. Station-wise extreme observation analysis
# ----------------------------------------------------------

print("\n6. STATION-WISE EXTREME OBSERVATIONS")

station_analysis = con.execute(f"""
    SELECT
        Station_ID,
        COUNT(*) AS total_records,
        MAX(SnowDepth) AS maximum_snow_depth,

        COUNT(*) FILTER (
            WHERE SnowDepth > 5000
        ) AS records_above_5000,

        COUNT(*) FILTER (
            WHERE SnowDepth > 10000
        ) AS records_above_10000

    FROM read_csv_auto('{DATASET_PATH}')

    GROUP BY Station_ID

    HAVING MAX(SnowDepth) > 5000

    ORDER BY maximum_snow_depth DESC
""").fetchdf()

print(station_analysis.head(20).to_string(index=False))

station_analysis.to_csv(
    os.path.join(OUTPUT_DIR, "station_extreme_analysis.csv"),
    index=False
)

# ----------------------------------------------------------
# 7. Save individual records above 10,000 mm
# ----------------------------------------------------------

print("\n7. SAVING RECORDS ABOVE 10,000 MM")

extreme_records = con.execute(f"""
    SELECT
        Station_ID,
        Date,
        SnowDepth,
        Latitude,
        Longitude
    FROM read_csv_auto('{DATASET_PATH}')
    WHERE SnowDepth > 10000
    ORDER BY SnowDepth DESC
""").fetchdf()

print("Records above 10,000 mm:", len(extreme_records))

extreme_records.to_csv(
    os.path.join(OUTPUT_DIR, "records_above_10000mm.csv"),
    index=False
)

# ----------------------------------------------------------
# 8. Completion
# ----------------------------------------------------------

con.close()

print("\nReports saved in:", OUTPUT_DIR)

print("\n" + "=" * 65)
print("DATA QUALITY ANALYSIS COMPLETED")
print("=" * 65)