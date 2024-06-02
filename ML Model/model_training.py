import tensorflow as tf
import numpy as np
from sklearn.model_selection import train_test_split
import data_preparation as data

# Create features and labels
def create_features_labels(df):
    X = df[['RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_middle', 'BB_lower']].values
    df['Future_Close'] = df['Close'].shift(-1)
    df.dropna(inplace=True)
    y = np.where(df['Future_Close'] > df['Close'], 1, 0)  # 1: Buy, 0: Sell
    
    # Ensure the lengths of X and y match
    X = X[:len(y)]
    
    return X, y

# Define the TensorFlow model
def build_model(input_shape):
    model = tf.keras.Sequential([
        tf.keras.layers.Input(shape=(input_shape,)),
        tf.keras.layers.Dense(64, activation='relu'),
        tf.keras.layers.Dense(32, activation='relu'),
        tf.keras.layers.Dense(1, activation='sigmoid')
    ])

    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model

# Example usage
symbol = 'AMD'
start_date = '2018-01-01'
end_date = '2023-01-01'
df = data.fetch_data(symbol, start_date, end_date)

X, y = create_features_labels(df)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
model = build_model(X_train.shape[1])
history = model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)
