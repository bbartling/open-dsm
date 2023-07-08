import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

# Load the dataset
df = pd.read_csv('./data/final.csv')
df['Date'] = pd.to_datetime(df['Date'])  # Convert 'Date' column to datetime if it's not already

# Set 'Date' column as the index
df.set_index('Date', inplace=True)

# Split the dataset into features (X) and target variable (y)
X = df.drop('action', axis=1)
y = df['action']

# Determine the index for splitting the data
split_index = int(len(df) * 0.8)  # 80% training, 20% testing

# Split the dataset into training and testing sets
X_train, X_test = X[:split_index], X[split_index:]
y_train, y_test = y[:split_index], y[split_index:]

# Create a Random Forest Classifier model
model = RandomForestClassifier()

# Train the model
model.fit(X_train, y_train)

# Make predictions on the testing set
y_pred = model.predict(X_test)

# Evaluate the accuracy of the model
accuracy = accuracy_score(y_test, y_pred)
print("Accuracy:", accuracy)
