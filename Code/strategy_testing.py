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
import csv


# Testing Parameters
symbol = 'AMD'
start_date = '2023-01-01'
end_date = '2023-12-31'
time_interval = '1d'

RSI_HIGH = 70
RSI_LOW = 30


# —————————————————————— Step 1: Fetch df ——————————————————————
ticker = 'AMD'
df = yf.download(symbol, start=start_date, end=end_date, interval=time_interval)

# —————————————————————— Step 2: Retrieve Indicators ——————————————————————

# Bollingner Bands
df['BB_upper'], df['BB_mid'], df['BB_lower'] = talib.BBANDS(df['Close'], timeperiod=20)

# MACD
df['MACD'], df['MACD_signal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)

# RSI
df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
df['RSI_ema'] = talib.EMA(df['RSI'], timeperiod=14)  # Calculate RSI-EMA

# Volume
df['Volume'] = df['Volume']
df.dropna(inplace=True)


# —————————————————————— Step 3: Implement Strategy ——————————————————————


# RSI
'''  
    If the RSI is above RSI_HIGH that means the stock is overbought
    If the RSI is below RSI_LOW that means the stock is underbought
    If the RSI is between RSI_HIGH aand RSI_LOW remain neutral

    Acceleration —> Direction —> Bullish (+) and Bearish (-)
    
    If the RSI goes above the RSI-EWMA & RSI[-1] is below RSI-EWMA —> Bullish
    If the RSI goes below the RSI-EWMA is above RSI-EWMA —> Bearish
'''
df['RSI_signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
for i in range(1,len(df)):
    # print("RSI",df['RSI'].iloc[i],"RSI ema",df['RSI_ema'].iloc[i])
    if df['RSI'].iloc[i] > df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] < df['RSI_ema'].iloc[i-1]:   # BUY
        df['RSI_signal'].iloc[i] = 1
        if df['RSI'].iloc[i] < RSI_LOW: df['RSI_signal'].iloc[i] = 2
    elif df['RSI'].iloc[i] < df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] > df['RSI_ema'].iloc[i-1]: # SELL
        df['RSI_signal'].iloc[i] = -1
        if df['RSI'].iloc[i] < RSI_LOW: df['RSI_signal'].iloc[i] = -2
    else:
        df['RSI_signal'].iloc[i] = 0
    

# MACD
'''  
    If the MACD flips from red to green with high volume that means —> Bullish
    If the MACD flips from green to red with high volume that means —> Bearish
    If the volume is decreasing that means the momentum is going down so prepare to close position.
'''
df['MACD_flip'] = 0
for i in range(1, len(df)):
    if df['MACD'].iloc[i] > df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] <= df['MACD_signal'].iloc[i-1]:
        df['MACD_flip'].iloc[i] = 1  # Flip from red to green
    elif df['MACD'].iloc[i] < df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] >= df['MACD_signal'].iloc[i-1]:
        df['MACD_flip'].iloc[i] = -1  # Flip from green to red
    # print(df['MACD_flip'])


# Bollinger Bands
'''  
    If the Bolligner Bands are divierging that means there is a large price movement. 

    MUCH MORE DIFFICULT TO IMPLEMENT
    1. Find average NORMALIZED level

'''
df['BB_width'] = df['BB_upper'] - df['BB_lower']
df['BB_diverging'] = 0
for i in range(1, len(df)):
    if df['BB_width'].iloc[i] > df['BB_width'].iloc[i-1]:
        df['BB_diverging'].iloc[i] = 1  # Bands are diverging
    elif df['BB_width'].iloc[i] < df['BB_width'].iloc[i-1]:
        df['BB_diverging'].iloc[i] = -1  # Bands are converging

# Deterimine BUY/SELL signal
df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
for i in range(len(df)):
    df['Signal'].iloc[i] = df['RSI_signal'].iloc[i] + df['RSI_signal'].iloc[i] + df['BB_diverging'].iloc[i]
    # df.loc[i, 'signal'] = df['RSI_signal'].iloc[i] + df['RSI_signal'].iloc[i] + df['BB_diverging'].iloc[i]



# ——————————————————————— Step 4: Analysis ——————————————————————— #
def calculate_profitability(data, profit_target_pct, stop_loss_pct, trade_size):
    trades = []
    position = 0  # 1 for long, -1 for short, 0 for no position
    entry_price = 0

    for i in range(len(data)):
        if position == 0:
            if data['Signal'].iloc[i] > 0:
                position = 1
                entry_price = data['Close'].iloc[i]
            elif data['Signal'].iloc[i] < 0:
                position = -1
                entry_price = data['Close'].iloc[i]
        elif position == 1:
            if data['Close'].iloc[i] >= entry_price * (1 + profit_target_pct / 100) or \
               data['Close'].iloc[i] <= entry_price * (1 - stop_loss_pct / 100):
                trades.append((entry_price, data['Close'].iloc[i], position))
                position = 0
        elif position == -1:
            if data['Close'].iloc[i] <= entry_price * (1 - profit_target_pct / 100) or \
               data['Close'].iloc[i] >= entry_price * (1 + stop_loss_pct / 100):
                trades.append((entry_price, data['Close'].iloc[i], position))
                position = 0

    profits = []
    for entry, exit, pos in trades:
        if pos == 1:
            profits.append((exit - entry) * trade_size / entry)
        elif pos == -1:
            profits.append((entry - exit) * trade_size / entry)

    return sum(profits), trades

# Calculate profitability
profit, trades = calculate_profitability(df, profit_target_pct=5, stop_loss_pct=2, trade_size=1000)

print(f"Total Profit: ${profit:.2f}")
print("Trades:")
for entry, exit, pos in trades:
    print(f"Entry: {entry}, Exit: {exit}, Position: {'Long' if pos == 1 else 'Short'}")


df.to_csv('technical_indicators.csv')       # export to CSV to analyze the data more easily

plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Close'], label='Close Price', color='blue')
plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['Close'], marker='^', color='g', label='Buy Signal')
plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['Close'], marker='v', color='r', label='Sell Signal')
plt.title('Buy and Sell Signals on AMD Historical Data')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()