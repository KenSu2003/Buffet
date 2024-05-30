import yfinance as yf
import pandas as pd
import numpy as np
import ta, talib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import classification_report, accuracy_score
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.utils import to_categorical
import matplotlib.pyplot as plt

# Testing Parameters
start_date = '2010-01-01'
end_date = '2023-12-31'
time_interval = '1d'

# Step 1: Fetch Data
ticker = 'AMD'
data = yf.download(ticker, start=start_date, end=end_date, interval=time_interval)

# —————————————————————— Step 2: Feature Engineering ——————————————————————

# Bollingner Bands
'''  
    If the Bolligner Bands are divierging that means there is a large price movement. 
'''
data['BB_high'] = ta.volatility.BollingerBands(data['Close']).bollinger_hband()
data['BB_low'] = ta.volatility.BollingerBands(data['Close']).bollinger_lband()

# MACD
'''  
    If the MACD flips from red to green with high volume that means strong buy.
    If the MACD flips from green to red with high volume that means strong sell.
    If the volume is decreasing that means the momentum is going down so prepare to close position.
'''
data['MACD'] = ta.trend.MACD(data['Close']).macd()
data['MACD_signal'] = ta.trend.MACD(data['Close']).macd_signal()

# RSI
data['RSI EWMA'] = ta.
data['RSI'] = ta.momentum.RSIIndicator(data['Close']).rsi()

# Volume
data['Volume'] = data['Volume']
data.dropna(inplace=True)

# Step 3: Label Creation
def create_labels(df, price_col='Close'):
    df['Signal'] = 0
    df.loc[(df['Close'] > df['BB_high']) & (df['MACD'] > df['MACD_signal']) & (df['RSI'] > 70), 'Signal'] = -1
    df.loc[(df['Close'] < df['BB_low']) & (df['MACD'] < df['MACD_signal']) & (df['RSI'] < 30), 'Signal'] = 1
    return df

data = create_labels(data)

# Step 4: Train-Test Split
X = data[['BB_high', 'BB_low', 'MACD', 'MACD_signal', 'RSI', 'Volume']]
y = data['Signal']

X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, shuffle=False)

# Standardize the data
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# One-hot encode the labels
y_train = to_categorical(y_train + 1)  # Adding 1 to make labels 0, 1, 2 instead of -1, 0, 1
y_test = to_categorical(y_test + 1)

# Step 5: Model Training
model = Sequential()
model.add(Dense(64, input_dim=X_train.shape[1], activation='relu'))
model.add(Dense(32, activation='relu'))
model.add(Dense(3, activation='softmax'))  # 3 classes: -1, 0, 1

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(X_train, y_train, epochs=50, batch_size=32, validation_split=0.2)

# Step 6: Model Evaluation
y_pred = model.predict(X_test)
y_pred_classes = np.argmax(y_pred, axis=1) - 1  # Converting back to -1, 0, 1
y_test_classes = np.argmax(y_test, axis=1) - 1

print("Accuracy:", accuracy_score(y_test_classes, y_pred_classes))
print("Classification Report:\n", classification_report(y_test_classes, y_pred_classes))

# Step 7: Visualization of model-predicted buy/sell signals on the historical chart
data_test = data.iloc[-len(y_test_classes):].copy()  # Ensure we are modifying a copy
data_test['Predicted_Signal'] = y_pred_classes

buy_signals = data_test[data_test['Predicted_Signal'] == 1]
sell_signals = data_test[data_test['Predicted_Signal'] == -1]

plt.figure(figsize=(14, 7))
plt.plot(data_test.index, data_test['Close'], label='Close Price')
plt.scatter(buy_signals.index, buy_signals['Close'], marker='^', color='g', label='Predicted Buy Signal', alpha=1)
plt.scatter(sell_signals.index, sell_signals['Close'], marker='v', color='r', label='Predicted Sell Signal', alpha=1)
plt.title('Predicted Buy and Sell Signals on AMD Historical Data')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()