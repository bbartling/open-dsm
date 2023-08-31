# algorithm

This code deploys a time-series forecasting approach for predicting electrical power consumption using a machine learning-based methodology. The multi-output forecasting model is trained on historical data and aims to forecast 60 future values based on input features derived from the time series.

The model operates by using the last 60 readings from the time series to predict the next 60-minute interval of electrical power. This ensures the model remains adaptive and responsive to the immediate past while predicting the near future.

The primary objective of this prediction mechanism is to actively manage or "curtail" adjustable electrical loads within a building. This predictive capability allows the system to make informed decisions and take proactive measures, ensuring the building aligns with Demand Side Management (DSM) goals.
 
### Example Algorithm Testing on Historical Data with `ml_forecast.py`
The visualization below represents historical data sourced from the process_raw_data directory. This data consists of one-minute sampled readings from an eGauge at a small commercial building in the upper Midwest USA equipped with a VAV air handling unit system and an air-cooled chiller.

The primary plot illustrates electrical power readings sampled every minute throughout a summer and the model's forecast 60 minutes into the future. Accompanying subplots offer a closer look at predictions made 60, 30, 15, and 5 minutes into the future, showcasing the model's forecasting granularity.

![Alt text](/algorithm_testing/plots/ml_forecast.png)

An additional zoomed-in plot hones in on the day with the highest electrical demand found in the dataset, offering a detailed perspective of the model's performance during peak consumption.

![Alt text](/algorithm_testing/plots/ml_forecast_zoomed.png)