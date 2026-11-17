import duckdb
import xgboost as xgb
import numpy as np
import os
import gc
import time

# =====================================
# 1. FILE PATHS
# =====================================

train_file = "F:/snow_model_train.parquet"
validation_file = "F:/snow_validation.parquet"

model_file = "F:/snow_xgboost_baseline.json"
metrics_file = "F:/snow_validation_metrics.txt"

os.makedirs("F:/duckdb_temp", exist_ok=True)

# =====================================
# 2. FEATURES
# =====================================

features = [
    "Latitude",
    "Longitude",

    "TB06_A", "TB06_D",
    "TB07_A", "TB07_D",
    "TB10_A", "TB10_D",
    "TB18_A", "TB18_D",
    "TB23_A", "TB23_D",
    "TB36_A", "TB36_D",
    "TB89_A", "TB89_D",

    "aspect",
    "slope",
    "tri",
    "elevation",

    "GR_36_18_A",
    "GR_36_18_D",
    "GR_89_36_A",
    "GR_89_36_D",

    "PR_06",
    "PR_18",
    "PR_36",
    "PR_89",

    "FD_89_18_A",
    "FD_36_18_A",
    "FD_23_10_A",

    "month_sin",
    "month_cos"
]

target = "SnowDepth"

print("Number of features:", len(features))

# =====================================
# 3. LOAD DATA USING DUCKDB
# =====================================

con = duckdb.connect()

con.execute("SET memory_limit = '8GB'")
con.execute("SET temp_directory = 'F:/duckdb_temp'")

def load_dataset(file_path):

    print("\nLoading:", file_path)

    month_expression = """
        CAST(
            SUBSTRING(CAST(Date AS VARCHAR), 5, 2)
            AS INTEGER
        )
    """

    feature_expressions = []

    for col in features:

        if col == "month_sin":
            expression = "SIN(2 * PI() * month / 12.0)"

        elif col == "month_cos":
            expression = "COS(2 * PI() * month / 12.0)"

        else:
            expression = f"COALESCE({col}, 'NaN'::DOUBLE)"

        feature_expressions.append(
            f"{expression} AS {col}"
        )

    query = f"""
        WITH base AS (
            SELECT *,
                {month_expression} AS month
            FROM read_parquet('{file_path}')
        )

        SELECT
            {', '.join(feature_expressions)},
            SnowDepth

        FROM base
    """

    data = con.execute(query).fetchnumpy()

    X = np.column_stack([
        data[col].astype(np.float32)
        for col in features
    ])

    y = data[target].astype(np.float32)

    del data
    gc.collect()

    print("Feature matrix:", X.shape)
    print("Target matrix:", y.shape)

    return X, y


# =====================================
# 4. LOAD TRAINING DATA
# =====================================

start_time = time.time()

X_train, y_train = load_dataset(train_file)

print("\nTraining data loaded.")

# =====================================
# 5. LOAD VALIDATION DATA
# =====================================

X_valid, y_valid = load_dataset(validation_file)

print("\nValidation data loaded.")

con.close()

# =====================================
# 6. CREATE QUANTILE MATRICES
# =====================================

print("\nCreating XGBoost matrices...")

dtrain = xgb.QuantileDMatrix(
    X_train,
    label=y_train,
    max_bin=256
)

dvalid = xgb.QuantileDMatrix(
    X_valid,
    label=y_valid,
    ref=dtrain,
    max_bin=256
)

del X_train, X_valid
del y_train, y_valid

gc.collect()

# =====================================
# 7. XGBOOST PARAMETERS
# =====================================

params = {
    "objective": "reg:squarederror",
    "eval_metric": "rmse",

    "tree_method": "hist",

    "max_depth": 8,
    "learning_rate": 0.05,

    "subsample": 0.8,
    "colsample_bytree": 0.8,

    "max_bin": 256,

    "nthread": 6,
    "seed": 42
}

# =====================================
# 8. TRAIN MODEL
# =====================================

print("\n========== TRAINING STARTED ==========")

model = xgb.train(
    params=params,

    dtrain=dtrain,

    num_boost_round=300,

    evals=[
        (dtrain, "train"),
        (dvalid, "validation")
    ],

    early_stopping_rounds=30,

    verbose_eval=10
)

print("\nTraining completed!")

# =====================================
# 9. VALIDATION PREDICTIONS
# =====================================

print("\nCalculating validation metrics...")

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

# =====================================
# 10. DISPLAY RESULTS
# =====================================

print("\n========== VALIDATION RESULTS ==========")

print("Best iteration:", model.best_iteration)

print("RMSE:", rmse)

print("MAE:", mae)

print("R2:", r2)

print("Training time:", round(time.time() - start_time, 2), "seconds")

# =====================================
# 11. SAVE MODEL
# =====================================

model.save_model(model_file)

with open(metrics_file, "w") as f:

    f.write("XGBoost Baseline Validation Results\n")
    f.write("-----------------------------------\n")

    f.write(f"Best iteration: {model.best_iteration}\n")
    f.write(f"RMSE: {rmse}\n")
    f.write(f"MAE: {mae}\n")
    f.write(f"R2: {r2}\n")

print("\nModel saved:", model_file)

print("Metrics saved:", metrics_file)

print("\nBASELINE MODEL COMPLETED!")