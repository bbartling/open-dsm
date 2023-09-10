# Demand Side Management System algorith on VOLTTRON agent

* NOT DONE incomplete

A comprehensive `PNNL VOLTTRON Agent` that integrates real-time power meter readings with predictive analytics to manage and optimize power consumption.

## Overview

### Data Collection:

- The power meter is read every 60 seconds.
- The reading, termed `current_power`, is cached for subsequent analytics.

### Cache Management:

- Maintains the most recent power readings.
- Oldest readings are removed to comply with the `CACHE_LIMIT`.

### Demand Response:

- Every 5 minutes, the system evaluates and adjusts the power consumption to meet set objectives.

### Rate of Change Analytics:

- After each power reading, the system calculates the rate of power change to detect spikes.
- A high rate indicates a surge in demand, prompting immediate action to reduce consumption.

### Predictive Modeling:

- Model is retrained daily using a `RandomForestRegressor`.
- Forecast predicts power consumption 60 minutes into the future.

### Proactive Adjustments Based on Forecasts:

- System uses the greater value between the current power reading and the 60-minute forecast to make decisions.
- Adjustments are made to ensure that power consumption remains within desired bounds.

## Workflow

### Minute 0:

- Power meter reading.
- Cache updated.
- Rate of change calculated.
- If rate of change exceeds set threshold, power consumption is immediately reduced.

### Minute 1-4:

- Power meter reading.
- Cache and rate of change updated.
- No other major action unless there's a detected spike.

### Minute 5:

- Power meter reading.
- Cache and rate of change updated.
- Adjusts power consumption based on average of recent readings.
- Retrains the model if a day has passed since the last training.
- Makes a 60-minute forecast.
- Decides on power adjustment based on forecast.

### Minute 6 and onwards:

- Loop repeats, with a model retrain only occurring once every 24 hours.

## Dependencies

- `pandas`: For efficient data handling and operations.
- `sklearn`: For the `RandomForestRegressor` and other potential ML tools.
