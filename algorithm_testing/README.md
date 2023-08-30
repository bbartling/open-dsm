# algorithm

The algorithm deployed in the code to forecast electrical power employs the Exponential Moving Average (EMA), a widely recognized statistical method to smooth time series data. EMA assigns greater weight to the most recent data points, making it particularly effective for real-time applications. In essence, EMA reduces the lag by applying more weight to recent values, allowing it to react more responsively to recent changes compared to a simple moving average.

In the context of this code, EMA operates on a selection of historical data points—specifically the last 60, 30, 15, and 5 readings—to produce a forecasted value of electrical power. By comparing these forecasted values with the actual real-time electrical power readings, the algorithm gauges the system's power consumption trends. Armed with these insights, the system can actively manage or "curtail" adjustable electrical loads within the building. The ultimate objective is to harness the predictive power of the EMA in tandem with real-time electrical readings, facilitating proactive measures to ensure the building aligns with Demand Side Management (DSM) goals.

 
### Example Algorithm Testing on Historical Data
This plot below represents the historical data from the `process_raw_data` directory of one minute sampled data from an eGauge at a small commercial building in the upper Midwest USA that contained a VAV air handling unit system and an air cooled chiller. The plot below attempts to deptict a summer of electrical power readings on the minute interval level and a forecasted 60 minutes into the future with EMA as well as subplots for the EMA on forecasting 60, 30, 15, and 5 minutes into the future.
![Alt text](/algorithm_testing/plots/ema_forecast.png)

This is a zoom plot of the highest demand day found in the dataset.
![Alt text](/algorithm_testing/plots/ema_forecast_zoomed.png)