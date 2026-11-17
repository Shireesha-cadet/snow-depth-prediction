import duckdb
import os

# ==========================================================
# SNOW DEPTH PREDICTION
# STEP 2: DATA CLEANING
# ==========================================================

INPUT_FILE = "F:/final_dataset_with_modis_fixed._wyomingcsv.csv"

# Separate output to avoid overwriting your existing dataset
OUTPUT_FILE = "F:/final_snow_depth_dataset_cleaned_reproduced.csv"

con = duckdb.connect()

con.execute("SET threads = 6")

print("=" * 65)
print("SNOW DEPTH DATA CLEANING")
print("=" * 65)

# ----------------------------------------------------------
# 1. Original dataset information
# ----------------------------------------------------------

print("\n1. ORIGINAL DATASET")

original_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_csv_auto('{INPUT_FILE}')
""").fetchone()[0]

print("Original rows:", f"{original_rows:,}")

# ----------------------------------------------------------
# 2. Remove unnecessary MODIS columns
# ----------------------------------------------------------

print("\n2. REMOVING MODIS COLUMNS")

columns_to_remove = [
    "LC_Type1",
    "Percent_Tree_Cover",
    "NDSI_Snow_Cover"
]

print("Columns removed:", columns_to_remove)

# ----------------------------------------------------------
# 3. Remove exact duplicate rows
# ----------------------------------------------------------

print("\n3. REMOVING EXACT DUPLICATES")

con.execute(f"""
    COPY (
        SELECT DISTINCT *
        EXCLUDE (
            LC_Type1,
            Percent_Tree_Cover,
            NDSI_Snow_Cover
        )
        FROM read_csv_auto('{INPUT_FILE}')
    )
    TO '{OUTPUT_FILE}'
    (HEADER, DELIMITER ',')
""")

print("Cleaned dataset created.")

# ----------------------------------------------------------
# 4. Verify cleaned dataset
# ----------------------------------------------------------

print("\n4. CLEANED DATASET VERIFICATION")

cleaned_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_csv_auto('{OUTPUT_FILE}')
""").fetchone()[0]

cleaned_columns = len(con.execute(f"""
    DESCRIBE SELECT *
    FROM read_csv_auto('{OUTPUT_FILE}')
""").fetchall())

print("Original rows:", f"{original_rows:,}")
print("Cleaned rows:", f"{cleaned_rows:,}")
print("Removed rows:", f"{original_rows - cleaned_rows:,}")
print("Cleaned columns:", cleaned_columns)

# ----------------------------------------------------------
# 5. Check remaining exact duplicates
# ----------------------------------------------------------

print("\n5. VERIFYING DUPLICATES")

remaining_duplicates = con.execute(f"""
    SELECT COUNT(*) -
           (SELECT COUNT(*) FROM (
               SELECT DISTINCT *
               FROM read_csv_auto('{OUTPUT_FILE}')
           ))
    FROM read_csv_auto('{OUTPUT_FILE}')
""").fetchone()[0]

print("Remaining exact duplicates:", remaining_duplicates)

# ----------------------------------------------------------
# 6. Check Station_ID-Date duplicates
# ----------------------------------------------------------

print("\n6. STATION-DATE DUPLICATE CHECK")

duplicate_groups = con.execute(f"""
    SELECT COUNT(*)
    FROM (
        SELECT Station_ID, Date
        FROM read_csv_auto('{OUTPUT_FILE}')
        GROUP BY Station_ID, Date
        HAVING COUNT(*) > 1
    )
""").fetchone()[0]

print("Duplicate Station_ID-Date groups:", duplicate_groups)

# ----------------------------------------------------------
# 7. Completion
# ----------------------------------------------------------

con.close()

print("\n" + "=" * 65)
print("DATA CLEANING COMPLETED")
print("=" * 65)