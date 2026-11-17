
import duckdb
import xgboost as xgb
import numpy as np
import gc

VALIDATION_FILE = "F:/snow_validation.parquet"
MODEL_FILE = "F:/snow_xgboost_baseline.json"

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

print("Loading validation data...")

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
    FROM read_parquet('{VALIDATION_FILE}')
)
SELECT
    {', '.join(expressions)},
    SnowDepth
FROM base
"""

data = con.execute(query).fetchnumpy()
con.close()

X = np.column_stack([
    data[col].astype(np.float32)
    for col in features
])

y = data["SnowDepth"].astype(np.float32)

del data
gc.collect()

print("Feature shape:", X.shape)
print("Target shape:", y.shape)

print("\nLoading saved model...")

model = xgb.Booster()
model.load_model(MODEL_FILE)

print("Best iteration:", model.best_iteration)
print("Boosting rounds:", model.num_boosted_rounds())

print("\nCreating DMatrix...")

dvalid = xgb.DMatrix(
    X,
    label=y,
    missing=np.nan
)

del X
gc.collect()

print("\nGenerating predictions...")

predictions = model.predict(
    dvalid,
    iteration_range=(0, model.best_iteration + 1)
)

actual = dvalid.get_label()

rmse = np.sqrt(np.mean((actual - predictions) ** 2))
mae = np.mean(np.abs(actual - predictions))

ss_res = np.sum((actual - predictions) ** 2)
ss_total = np.sum((actual - np.mean(actual)) ** 2)

r2 = 1 - (ss_res / ss_total)

print("\n========== DMatrix VERIFICATION RESULTS ==========")
print("RMSE:", rmse)
print("MAE:", mae)
print("R2:", r2)
print("Records:", len(actual))
