## Testing Electricity Value Prediction using Tree Regression

This script leverages decision tree regression and multi-output regression to forecast electricity consumption values where the idea is to test different models and approaches to embedd inside a BACnet app.

## Requirements
- Python (>=3.6)
- scikit-learn
- pandas
- numpy
- matplotlib

## Installation
1. **pip install Python libraries**

```bash
pip install scikit-learn pandas numpy matplotlib

```

2. **Tested on Windows**
```bash
python electricity_prediction.py --corr <correlation_threshold>
```
Replace <correlation_threshold> with the desired correlation threshold for feature selection. The script will train a decision tree regression model using the provided data and correlation threshold. After training, the script will make predictions for future electricity consumption values and generate plots for visualization.

3. **Command-line Arguments**
* `--corr`: Correlation threshold for feature selection (default: 0.99).
* Best results were found with a `.9` value used for `--core` where values of `.99, .9, .8, .7, .6, .5` where all tested. See Feature Selection directly below for more details. 

## Feature Selection
Before training the model, the script performs feature selection based on a correlation threshold. 
The idea or theory is to remove highly correlated data to hopefully achieve better results. 
If this is built into a BACnet app this would run under the hood where if highly correlated data was being written
to the BACnet API this type of code would remove it automatically.
Here's a breakdown of the feature selection steps:

1. **Compute Correlation Matrix:** The script computes the absolute correlation matrix for the provided data.
```python
# Compute the absolute correlation matrix
correlation_matrix = df.corr().abs()
```
2. **Select Features to Drop:** It identifies features that have a correlation greater than the specified threshold (CORRELATION) with other features. These features are considered for removal.
```python
# Select the upper triangle of the correlation matrix
upper = correlation_matrix.where(
    np.triu(np.ones(correlation_matrix.shape), k=1).astype(bool)
)

features_to_check_for_correlation = df.drop(columns=["main_power_watts"]).columns
to_drop = [
    column
    for column in upper.columns
    if any(upper[column] > CORRELATION) and column in features_to_check_for_correlation
]
```
3. **Remove Features:** The identified features are then dropped from the DataFrame.
```python
# Drop features from the dataframe
df = df.drop(columns=to_drop, errors="ignore")
```

What you will notice in the console is the columns automatically being dropped for the target col below `main_power_watts` it was found 
the columns `PV Inverter 2 Watts` and `PV Inverter 3 Watts` were highly correlated and they will automatically be removed from pandas df:
```bash
Index(['RTU Cooling Capacity Status', 'main_power_watts',
       'RTU Outdoor Air Temperature BAS', 'RTU Discharge Air Temperature',
       'RTU Mixed Air Temperature Local', 'RTU Return Air Temperature',
       'RTU Duct Static Pressure Local', 'Supply Fan Speed Command',
       'BOILER System Pump VFD Signal', 'RTU Space Temperature BAS',
       'BOILER Hot Water Return Temperature',
       'BOILER Hot Water Supply Temperature', 'PV Inverter 1 Watts',
       'PV Inverter 2 Watts', 'PV Inverter 3 Watts'],
      dtype='object')
DOING CORR:  0.99
Cols to drop 
 ['PV Inverter 2 Watts', 'PV Inverter 3 Watts']
 ```

## Model Training
After feature selection, the script proceeds with model training using decision tree regression and multi-output regression. Here's how it's done:

1. **Time Series Split for Validation:** To ensure robust validation, the script employs TimeSeriesSplit with 5 splits to create training and validation sets.

```python
# Time series split for validation
tscv = TimeSeriesSplit(n_splits=5)
```
2. **Model Definition:** It wraps the DecisionTreeRegressor with MultiOutputRegressor to handle multiple output predictions.
```python
# Wrap DecisionTreeRegressor for multi-output regression
model = MultiOutputRegressor(DecisionTreeRegressor(random_state=0))
```
3. **Hyperparameter Grid for Grid Search:** The script defines a parameter grid for hyperparameter tuning of the decision tree regressor. You may adjust these parameters for testing purposes. The BACnet app will run this same pipeline to select best hyperparameters.
```python
# Parameter grid for DecisionTreeRegressor (example parameters, you'll need to define these yourself)
parameter_grid = {
    "estimator__max_depth": [None, 10, 20, 30],
    "estimator__min_samples_split": [2, 5, 10],
    "estimator__min_samples_leaf": [1, 2, 4],
}
```
4. **Time Series Cross-Validation:** It sets up TimeSeriesSplit for cross-validation, which will be used for grid search.
```python
# Time Series Cross Validator
time_series_cv = TimeSeriesSplit(n_splits=5).split(X)
```
5. **Grid Search:** The script performs a grid search with cross-validation to find the best model based on the negative mean squared error.
```python
# Grid Search with time series cross-validation
grid_search = GridSearchCV(
    model, parameter_grid, cv=time_series_cv, scoring="neg_mean_squared_error"
)
```

## Plots 
* The load profile on the 3rd highest power day appeared to be the best.
* See `analysis.py` for the correlation matrix plot.

![Alt text](/time_series_testing/DecisionTreeRegressor_corr.png)
![Alt text](/time_series_testing/ExtraTreeRegressor_corr.png)
![Alt text](/time_series_testing/correlation_matrix.png)