# Dataset Information

This directory contains information about the datasets used in the Snow Depth Prediction Using Microwave Signals project.

## Data Sources

The project uses the following data sources:

1. **AMSR-2 Passive Microwave Data**
   - Provides satellite brightness temperature observations.
   - Used to extract microwave signals related to snow conditions.

2. **GHCN-Daily**
   - Provides ground-based weather station observations.
   - Used to obtain measured snow depth values.
   - Snow depth is the target variable for prediction.

3. **Terrain Data**
   - Includes elevation, slope, aspect, and terrain ruggedness index (TRI).
   - Provides geographical information for model training.

## Dataset Description

The combined dataset contains:

- 7,747,796 original records.
- 34,470 unique weather stations.
- Observations from January 2013 to April 2026.
- Snow depth measurements in millimetres.

After removing selected MODIS-related columns and exact duplicate records:

- 7,688,655 records remain.
- 34 columns remain.

## Why Are the Dataset Files Not Included?

The original combined dataset is approximately 2.84 GB.

Large raw and processed datasets are not included in this GitHub repository to avoid unnecessary repository size.

The preprocessing scripts used to inspect, clean, analyze, engineer features, and split the dataset are available in:

`src/preprocessing/`

## Generated Dataset Files

The preprocessing pipeline generates the following files:

| Dataset | Description |
|---|---|
| `final_snow_depth_dataset_cleaned_reproduced.csv` | Cleaned dataset |
| `snow_dataset_feature_engineered.parquet` | Dataset with seasonal features |
| `snow_model_train.parquet` | Model training data |
| `snow_validation.parquet` | Validation data |
| `snow_test.parquet` | Testing data |

These files are generated locally and are not committed to GitHub.