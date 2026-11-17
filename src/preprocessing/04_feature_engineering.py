
import duckdb
import os

# ==========================================================
# SNOW DEPTH PREDICTION
# STEP 4: FEATURE ENGINEERING
# ==========================================================

INPUT_FILE = "F:/final_snow_depth_dataset_cleaned_reproduced.csv"

OUTPUT_FILE = "F:/snow_dataset_feature_engineered.parquet"

con = duckdb.connect()

con.execute("SET threads = 6")

print("=" * 65)
print("SNOW DEPTH FEATURE ENGINEERING")
print("=" * 65)

# ----------------------------------------------------------
# 1. Load cleaned dataset
# ----------------------------------------------------------

print("\n1. LOADING CLEANED DATASET")

total_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_csv_auto('{INPUT_FILE}')
""").fetchone()[0]

print("Total records:", f"{total_rows:,}")

# ----------------------------------------------------------
# 2. Extract month and create cyclic features
# ----------------------------------------------------------

print("\n2. CREATING SEASONAL FEATURES")

con.execute(f"""
    COPY (
        SELECT
            *,
            SIN(
                2 * PI() *
                (CAST(SUBSTRING(CAST(Date AS VARCHAR), 5, 2) AS INTEGER) - 1)
                / 12.0
            ) AS month_sin,

            COS(
                2 * PI() *
                (CAST(SUBSTRING(CAST(Date AS VARCHAR), 5, 2) AS INTEGER) - 1)
                / 12.0
            ) AS month_cos

        FROM read_csv_auto('{INPUT_FILE}')
    )
    TO '{OUTPUT_FILE}'
    (FORMAT PARQUET)
""")

print("Month extracted from Date.")
print("month_sin created.")
print("month_cos created.")

# ----------------------------------------------------------
# 3. Verify engineered dataset
# ----------------------------------------------------------

print("\n3. VERIFYING FEATURE-ENGINEERED DATASET")

result = con.execute(f"""
    SELECT
        COUNT(*) AS total_records,
        COUNT(month_sin) AS month_sin_count,
        COUNT(month_cos) AS month_cos_count,
        MIN(month_sin) AS minimum_month_sin,
        MAX(month_sin) AS maximum_month_sin,
        MIN(month_cos) AS minimum_month_cos,
        MAX(month_cos) AS maximum_month_cos
    FROM read_parquet('{OUTPUT_FILE}')
""").fetchdf()

print(result.to_string(index=False))

# ----------------------------------------------------------
# 4. Display final feature columns
# ----------------------------------------------------------

print("\n4. FINAL FEATURE COLUMNS")

columns = con.execute(f"""
    DESCRIBE SELECT *
    FROM read_parquet('{OUTPUT_FILE}')
""").fetchdf()

print(columns[["column_name", "column_type"]].to_string(index=False))

# ----------------------------------------------------------
# 5. Completion
# ----------------------------------------------------------

con.close()

print("\nFeature-engineered dataset saved at:")
print(OUTPUT_FILE)

print("\n" + "=" * 65)
print("FEATURE ENGINEERING COMPLETED")
print("=" * 65)
