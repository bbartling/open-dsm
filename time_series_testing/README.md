# Time Series Forecasting with LSTM

This directory contains code for time series forecasting using Long Short-Term Memory (LSTM) networks us `tf.keras` library which can run a type of recurrent neural network (RNN) capable of learning long-term dependencies in data sequences. This project is focused on forecasting future values of a time series given past observations.
 
### LSTM

LSTM networks are a type of RNN that include memory cells capable of maintaining information in memory for long periods of time. They are particularly useful for time series forecasting because they can learn from sequences of data and predict future values based on patterns and trends found in the data.


### Data Preprocessing

The preprocess_data function is an essential step in preparing the time series data for training the LSTM network. This function takes in the raw data, the sequence length (number of past observations to consider), and the prediction length (number of future values to predict) as input and returns the processed data in the form of input sequences (X) and target sequences (y).

```python
def preprocess_data(data, seq_length, pred_length):
    X, y = [], []
    for i in range(seq_length, len(data) - pred_length):
        X.append(data[i - seq_length:i, 0])
        y.append(data[i: i + pred_length, 0])
    return np.array(X), np.array(y)
```

In this function, we create sequences of data by sliding a window of length seq_length over the time series data, with each window's last value being used as a starting point for the next window. For each window, we also gather the corresponding future values of length pred_length as the target sequence. This way, we generate pairs of input sequences and their corresponding target sequences, which will be used to train the LSTM network.

### Sequential Fitting

In the training loop, we utilize a sequential fitting approach, where we repeatedly train the model on the data while adjusting the model's hyperparameters to optimize its performance. This allows us to iteratively improve the model's accuracy in predicting future values of the time series.

```python
for seq_length in sequence_lengths:
```

### Best Model Callback

The best model callback is a technique used to save the model that performs best on the validation data during training. This is achieved using the ModelCheckpoint callback from Keras, which monitors a specified metric (e.g., validation loss) and saves the model that achieves the best performance on that metric.

```python
best_model_save = ModelCheckpoint('best_model.h5', save_best_only=True, monitor='val_loss', mode='min')
```
By using this callback, we can ensure that we retain the model with the highest predictive accuracy, which can then be loaded and used for future predictions or further analysis.

