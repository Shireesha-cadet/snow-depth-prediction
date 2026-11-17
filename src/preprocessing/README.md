# Snow Depth Prediction – Data Preprocessing

This directory contains the preprocessing scripts used in the **Snow Depth Prediction Using Microwave Signals** project.

The objective of preprocessing is to inspect, clean, analyze, prepare features, and split the dataset before training the XGBoost regression model.

## Dataset Overview

**Input dataset:** `final_dataset_with_modis_fixed._wyomingcsv.csv`

- Original records: 7,747,796
- Original columns: 37
- Unique stations: 34,470
- Date range: January 2013 – April 2026
- Target variable: `SnowDepth`
- Target unit: millimetres (mm)

## Preprocessing Workflow

Execute the scripts in the following order.

### 1. Data Inspection

**Script:** `01_data_inspection.py`

Purpose:
- Inspect dataset dimensions and column names.
- Identify missing values.
- Count exact duplicate rows.
- Identify duplicate station-date combinations.
- Analyze SnowDepth statistics.
- Examine geographical and temporal coverage.
- Identify extreme SnowDepth observations.

This step helps understand the dataset before making modifications.

### 2. Data Cleaning

**Script:** `02_data_cleaning.py`

Purpose:
- Remove the following MODIS-related columns:
  - `LC_Type1`
  - `Percent_Tree_Cover`
  - `NDSI_Snow_Cover`
- Remove exact duplicate rows.
- Verify the cleaned dataset.

**Output:** `final_snow_depth_dataset_cleaned_reproduced.csv`

Results:
- Original records: 7,747,796
- Cleaned records: 7,688,655
- Exact duplicate rows removed: 59,141
- Final columns: 34
- Remaining exact duplicate rows: 0

### 3. Data Quality Analysis

**Script:** `03_data_quality_analysis.py`

Purpose:
- Analyze missing values.
- Calculate SnowDepth descriptive statistics.
- Identify potential outliers using the IQR method.
- Count observations above different SnowDepth thresholds.
- Analyze stations containing extreme observations.
- Export records with SnowDepth above 10,000 mm for further investigation.

Reports are saved in:

`F:/snow_data_quality_reports/`

Important:
- Potential outliers are identified for investigation.
- Extreme observations are not automatically deleted.
- Missing values are not imputed in this step.
- XGBoost supports missing feature values natively.

### 4. Feature Engineering

**Script:** `04_feature_engineering.py`

Purpose:

Create seasonal features from the month extracted from the `Date` column.

Two cyclic features are generated:

**Month sine:**

`month_sin = sin(2 × π × (month - 1) / 12)`

**Month cosine:**

`month_cos = cos(2 × π × (month - 1) / 12)`

Using sine and cosine represents the cyclic relationship between months. For example, December and January are close in the seasonal cycle.

Other features, including brightness temperatures and GR, PR, and FD features, are already present in the cleaned dataset.

**Output:** `F:/snow_dataset_feature_engineered.parquet`

Results:
- Records: 7,688,655
- Columns: 36
- New features: `month_sin`, `month_cos`

### 5. Station-Wise Data Splitting

**Script:** `05_data_splitting.py`

Purpose:

Split the dataset based on `Station_ID` so that observations from the same station do not appear in multiple datasets.

**First split:**
- 80% station groups → training pool
- 20% station groups → testing

**Second split:**
- 90% of the training pool → model training
- 10% of the training pool → validation

The splits use DuckDB hash-based station assignment.

**Output directory:** `F:/snow_reproduced_splits/`

| Dataset | Records | Unique Stations |
|---|---:|---:|
| Model Training | 5,520,389 | 24,750 |
| Validation | 612,067 | 2,737 |
| Testing | 1,556,199 | 6,983 |
| **Total** | **7,688,655** | **34,470** |

Verification:
- No overlapping stations between training and validation.
- No overlapping stations between training and testing.
- No overlapping stations between validation and testing.
- All records are accounted for after splitting.

Note: Station-wise splitting evaluates generalization to unseen station IDs. It does not necessarily guarantee geographical separation between the datasets.

## Project Structure

```text
snow-depth-prediction/
│
├── src/
│   ├── preprocessing/
│   │   ├── 01_data_inspection.py
│   │   ├── 02_data_cleaning.py
│   │   ├── 03_data_quality_analysis.py
│   │   ├── 04_feature_engineering.py
│   │   ├── 05_data_splitting.py
│   │   └── README.md
│   │
│   ├── train_xgboost.py
│   ├── evaluate_xgboost.py
│   └── verify_validation.py
│
├── models/
├── results/
├── requirements.txt
└── README.md
```

## Execution Order

Run the preprocessing scripts in this order:

```bash
python src/preprocessing/01_data_inspection.py

python src/preprocessing/02_data_cleaning.py

python src/preprocessing/03_data_quality_analysis.py

python src/preprocessing/04_feature_engineering.py

python src/preprocessing/05_data_splitting.py
```

## Important Notes

- The original dataset is preserved.
- The original trained XGBoost model is not modified.
- The preprocessing scripts generate separate output files.
- Large datasets are not included in the GitHub repository.
- DuckDB 1.5.5 is used for data processing and hash-based splitting.
- Reproducing the split requires the same DuckDB hash behavior and split expressions.