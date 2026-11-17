\# Snow Depth Prediction Using Microwave Signals



\## Project Overview



Snow depth is an important environmental parameter for water resource management, climate studies, and understanding snow accumulation.



Ground-based weather stations provide direct snow depth measurements, but these stations are sparsely distributed across many geographical regions.



This project uses passive satellite microwave observations, ground-based snow depth measurements, and geographical terrain features to develop a machine learning model for snow depth prediction.



The primary objective is to investigate how satellite microwave signals can help estimate snow depth across different geographical locations.



\## Dataset Information



The dataset combines information from:



\- \*\*AMSR-2:\*\* Passive microwave brightness temperature observations.

\- \*\*GHCN-Daily:\*\* Ground-based snow depth measurements.

\- \*\*Terrain data:\*\* Elevation, slope, aspect, and terrain ruggedness index (TRI).



\### Dataset Statistics



| Description | Value |

|---|---:|

| Total records | 7,688,655 |

| Unique weather stations | 34,470 |

| Date range | January 2013 – April 2026 |

| Number of columns | 34 |

| Target variable | SnowDepth (mm) |



The original dataset is not included in this repository because of its large size.



\## Features Used



The model uses 33 input features.



\### 1. Geographical Features

\- Latitude

\- Longitude



\### 2. Microwave Brightness Temperature Features

\- TB06\_A, TB06\_D

\- TB07\_A, TB07\_D

\- TB10\_A, TB10\_D

\- TB18\_A, TB18\_D

\- TB23\_A, TB23\_D

\- TB36\_A, TB36\_D

\- TB89\_A, TB89\_D



\### 3. Terrain Features

\- Elevation

\- Slope

\- Aspect

\- TRI (Terrain Ruggedness Index)



\### 4. Derived Microwave Features

\- GR (Gradient Ratio)

\- PR (Polarization Ratio)

\- FD (Frequency Difference)



\### 5. Seasonal Features

\- month\_sin

\- month\_cos



\## Data Preprocessing



\- Removed unnecessary MODIS-related columns.

\- Removed exact duplicate records.

\- Checked missing values and data quality.

\- Preserved missing feature values for XGBoost's native missing-value handling.

\- Created training, validation, and testing datasets using station-wise splitting.



The Station\_ID groups in the training, validation, and testing datasets are separate.



\## Model Development



\*\*Algorithm:\*\* XGBoost Regressor



\### Model Configuration



| Parameter | Value |

|---|---:|

| Objective | reg:squarederror |

| Evaluation metric | RMSE |

| Tree method | hist |

| Maximum depth | 8 |

| Learning rate | 0.05 |

| Subsample | 0.8 |

| Column sample by tree | 0.8 |

| Maximum bins | 256 |

| Boosting rounds | 300 |



The model was trained using 33 input features.



\## Model Performance



\### Validation Results



| Metric | Result |

|---|---:|

| RMSE | 277.06 mm |

| MAE | 167.18 mm |

| R² | 0.6411 |



Validation records: 612,067



\### Independent Test Results



| Metric | Result |

|---|---:|

| RMSE | 292.43 mm |

| MAE | 167.07 mm |

| R² | 0.5393 |



Test records: 1,556,199



\### Evaluation Metrics



\- \*\*RMSE:\*\* Measures the square root of the average squared prediction error.

\- \*\*MAE:\*\* Measures the average absolute difference between actual and predicted snow depth.

\- \*\*R²:\*\* Measures how much variation in snow depth is explained by the model.



All snow depth measurements and error metrics are expressed in millimetres.



\## Train, Validation and Test Strategy



The dataset was divided based on Station\_ID to prevent the same station from appearing in multiple splits.



| Dataset | Stations | Records |

|---|---:|---:|

| Training | 24,750 | 5,520,389 |

| Validation | 2,737 | 612,067 |

| Testing | 6,983 | 1,556,199 |



This setup evaluates performance on unseen station IDs within the geographical coverage represented in the dataset.



It does not establish generalization to entirely unseen geographical regions.



\## Technologies Used



\- Python

\- XGBoost

\- NumPy

\- Pandas

\- DuckDB

\- Scikit-learn



\## Repository Structure



```text

snow-depth-prediction/

│

├── data/

│   └── README.md

│

├── models/

│   └── snow\_xgboost\_baseline.json

│

├── notebooks/

│

├── results/

│   ├── validation\_metrics.txt

│   └── test\_metrics.txt

│

├── src/

│   ├── train\_xgboost.py

│   ├── evaluate\_xgboost.py

│   └── verify\_validation.py

│

├── README.md

├── requirements.txt

└── .gitignore

```



\## Future Work



\- Compare global and regional XGBoost models.

\- Investigate spatial validation strategies.

\- Evaluate geographical generalization.

\- Explore further model performance improvements.



\## Project Status



The global XGBoost baseline model has been trained and evaluated using separate training, validation, and testing station groups.



Further experiments will focus on comparing global and regional models and investigating geographical generalization.

