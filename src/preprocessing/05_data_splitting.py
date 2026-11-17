import duckdb
import os

# ==========================================================
# SNOW DEPTH PREDICTION
# STEP 5: STATION-WISE DATA SPLITTING
# ==========================================================

INPUT_FILE = "F:/snow_dataset_feature_engineered.parquet"

OUTPUT_DIR = "F:/snow_reproduced_splits"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Output files
TRAIN_POOL = f"{OUTPUT_DIR}/snow_train_pool.parquet"
MODEL_TRAIN = f"{OUTPUT_DIR}/snow_model_train.parquet"
VALIDATION = f"{OUTPUT_DIR}/snow_validation.parquet"
TEST = f"{OUTPUT_DIR}/snow_test.parquet"

con = duckdb.connect()

con.execute("SET threads = 6")

print("=" * 65)
print("STATION-WISE DATA SPLITTING")
print("=" * 65)

# ----------------------------------------------------------
# 1. Check input dataset
# ----------------------------------------------------------

print("\n1. CHECKING INPUT DATASET")

total_rows = con.execute(f"""
    SELECT COUNT(*)
    FROM read_parquet('{INPUT_FILE}')
""").fetchone()[0]

total_stations = con.execute(f"""
    SELECT COUNT(DISTINCT Station_ID)
    FROM read_parquet('{INPUT_FILE}')
""").fetchone()[0]

print("Total records:", f"{total_rows:,}")
print("Unique stations:", f"{total_stations:,}")

# ----------------------------------------------------------
# 2. First split: Training pool and testing
# ----------------------------------------------------------

print("\n2. CREATING TRAINING POOL AND TEST DATA")

# Same station-wise hash rule used in the original split.
# Stations with hash % 5 == 0 go to testing.
# Remaining stations go to the training pool.

con.execute(f"""
    COPY (
        SELECT *
        FROM read_parquet('{INPUT_FILE}')
        WHERE hash(Station_ID) % 5 != 0
    )
    TO '{TRAIN_POOL}'
    (FORMAT PARQUET)
""")

con.execute(f"""
    COPY (
        SELECT *
        FROM read_parquet('{INPUT_FILE}')
        WHERE hash(Station_ID) % 5 = 0
    )
    TO '{TEST}'
    (FORMAT PARQUET)
""")

print("Training pool and test dataset created.")

# ----------------------------------------------------------
# 3. Second split: Model training and validation
# ----------------------------------------------------------

print("\n3. SPLITTING TRAINING POOL")

# Same validation hash rule used in the original split.
# 10% of training-pool stations go to validation.
# Remaining stations go to model training.

con.execute(f"""
    COPY (
        SELECT *
        FROM read_parquet('{TRAIN_POOL}')
        WHERE hash(Station_ID || '_validation') % 10 != 0
    )
    TO '{MODEL_TRAIN}'
    (FORMAT PARQUET)
""")

con.execute(f"""
    COPY (
        SELECT *
        FROM read_parquet('{TRAIN_POOL}')
        WHERE hash(Station_ID || '_validation') % 10 = 0
    )
    TO '{VALIDATION}'
    (FORMAT PARQUET)
""")

print("Model training and validation datasets created.")

# ----------------------------------------------------------
# 4. Verify record counts
# ----------------------------------------------------------

print("\n4. VERIFYING SPLIT SIZES")

files = {
    "Training pool": TRAIN_POOL,
    "Model training": MODEL_TRAIN,
    "Validation": VALIDATION,
    "Testing": TEST
}

for name, path in files.items():

    rows, stations = con.execute(f"""
        SELECT
            COUNT(*),
            COUNT(DISTINCT Station_ID)
        FROM read_parquet('{path}')
    """).fetchone()

    print(f"\n{name}")
    print("Records:", f"{rows:,}")
    print("Stations:", f"{stations:,}")

# ----------------------------------------------------------
# 5. Verify station separation
# ----------------------------------------------------------

print("\n5. CHECKING STATION OVERLAP")

overlap_checks = [
    ("Training vs Validation", MODEL_TRAIN, VALIDATION),
    ("Training vs Testing", MODEL_TRAIN, TEST),
    ("Validation vs Testing", VALIDATION, TEST)
]

for name, file1, file2 in overlap_checks:

    overlap = con.execute(f"""
        SELECT COUNT(*)
        FROM (
            SELECT DISTINCT Station_ID
            FROM read_parquet('{file1}')
        ) a
        INNER JOIN (
            SELECT DISTINCT Station_ID
            FROM read_parquet('{file2}')
        ) b
        ON a.Station_ID = b.Station_ID
    """).fetchone()[0]

    print(f"{name}: {overlap} overlapping stations")

# ----------------------------------------------------------
# 6. Check total record consistency
# ----------------------------------------------------------

print("\n6. CHECKING TOTAL RECORD CONSISTENCY")

split_total = sum(
    con.execute(f"""
        SELECT COUNT(*)
        FROM read_parquet('{path}')
    """).fetchone()[0]
    for path in [MODEL_TRAIN, VALIDATION, TEST]
)

print("Original records:", f"{total_rows:,}")
print("Records after splitting:", f"{split_total:,}")

if total_rows == split_total:
    print("SUCCESS: All records accounted for.")
else:
    print("WARNING: Record counts do not match.")

con.close()

print("\nOutput directory:", OUTPUT_DIR)

print("\n" + "=" * 65)
print("DATA SPLITTING COMPLETED")
print("=" * 65)