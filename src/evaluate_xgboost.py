import duckdb
import xgboost as xgb
import numpy as np
import time
import gc

# =====================================
# FILE PATHS
# =====================================

test_file = "F:/snow_test.parquet"
model_file = "F:/snow_xgboost_baseline.json"

# =====================================
# FEATURES
# =====================================

features = [
    "Latitude", "Longitude",

    "TB06_A", "TB06_D",
    "TB07_A", "TB07_D",
    "TB10_A", "TB10_D",
    "TB18_A", "TB18_D",
    "TB23_A", "TB23_D",
    "TB36_A", "TB36_D",
    "TB89_A", "TB89_D",

    "aspect", "slope", "tri", "elevation",

    "GR_36_18_A", "GR_36_18_D",
    "GR_89_36_A", "GR_89_36_D",

    "PR_06", "PR_18", "PR_36", "PR_89",

    "FD_89_18_A", "FD_36_18_A", "FD_23_10_A",

    "month_sin", "month_cos"
]

# =====================================
# LOAD TEST DATA
# =====================================

print("Loading test dataset...")

con = duckdb.connect()

con.execute("SET memory_limit = '8GB'")
con.execute("SET temp_directory = 'F:/duckdb_temp'")

month_expression = """
CAST(
    SUBSTRING(CAST(Date AS VARCHAR), 5, 2)
    AS INTEGER
)
"""

expressions = []

for col in features:

    if col == "month_sin":
        expression = "SIN(2 * PI() * month / 12.0)"

    elif col == "month_cos":
        expression = "COS(2 * PI() * month / 12.0)"

    else:
        expression = f"COALESCE({col}, 'NaN'::DOUBLE)"

    expressions.append(f"{expression} AS {col}")

query = f"""
WITH base AS (
    SELECT *,
        {month_expression} AS month
    FROM read_parquet('{test_file}')
)

SELECT
    {', '.join(expressions)},
    SnowDepth

FROM base
"""

start = time.time()

data = con.execute(query).fetchnumpy()

X_test = np.column_stack([
    data[col].astype(np.float32)
    for col in features
])

y_test = data["SnowDepth"].astype(np.float32)

del data
gc.collect()

con.close()

print("Test feature matrix:", X_test.shape)
print("Test target:", y_test.shape)

# =====================================
# LOAD TRAINED MODEL
# =====================================

print("\nLoading trained model...")

model = xgb.Booster()
model.load_model(model_file)

# =====================================
# PREDICTIONS
# =====================================

print("\nGenerating predictions...")

dtest = xgb.DMatrix(
    X_test,
    missing=np.nan
)

predictions = model.predict(
    dtest,
    iteration_range=(0, model.best_iteration + 1)
)

# =====================================
# EVALUATION METRICS
# =====================================

rmse = np.sqrt(np.mean((y_test - predictions) ** 2))

mae = np.mean(np.abs(y_test - predictions))

ss_res = np.sum((y_test - predictions) ** 2)

ss_total = np.sum((y_test - np.mean(y_test)) ** 2)

r2 = 1 - (ss_res / ss_total)

# =====================================
# RESULTS
# =====================================

print("\n========== FINAL TEST RESULTS ==========")

print("RMSE:", rmse)
print("MAE:", mae)
print("R2:", r2)

print("\nTest records:", len(y_test))

print("Evaluation time:", round(time.time() - start, 2), "seconds")

# =====================================
# SAVE RESULTS
# =====================================

with open("F:/snow_test_metrics.txt", "w") as f:

    f.write("XGBoost Baseline Test Results\n")
    f.write("-----------------------------\n")

    f.write(f"RMSE: {rmse}\n")
    f.write(f"MAE: {mae}\n")
    f.write(f"R2: {r2}\n")

    f.write(f"Test records: {len(y_test)}\n")

print("\nResults saved to F:/snow_test_metrics.txt")

print("\nTEST EVALUATION COMPLETED!")