import yfinance as yf
import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
import csv

import strategy1

# Testing Parameters
symbol = 'AMD'
start_date = '2021-01-01'   # default = 2023-01-01 , profit: 622.77
end_date = '2023-12-31'     # default = 2023-12-31
time_interval = '1d'

RSI_HIGH = 70
RSI_LOW = 30
POSITION_SIZE = 1000    #in USD
TAKE_PROFIT = 5         # in %  (default)5%: +$683.67, 10%: +$277.29
STOP_LOSS = 5           # in %  (default)1%: +$602.70, 5%: +$136.19


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
df = strategy1.calc_RSI(df, RSI_HIGH, RSI_LOW)
    
# MACD
df = strategy1.calc_MACD(df)

# Bollinger Bands
df = strategy1.calc_BB(df)

# Deterimine BUY/SELL signal
df = strategy1.trade(df)


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
profit, trades = calculate_profitability(df, profit_target_pct=TAKE_PROFIT, stop_loss_pct=STOP_LOSS, trade_size=POSITION_SIZE)

print(f"Total Profit: ${profit:.2f}")
print("Trades:")
for entry, exit, pos in trades:
    print(f"Entry: {entry}, Exit: {exit}, Position: {'Long' if pos == 1 else 'Short'}")


# Save data to csv file
df.to_csv('technical_indicators.csv')       # export to CSV to analyze the data more easily


# Plot the trade signals
plt.figure(figsize=(14, 7))
plt.plot(df.index, df['Close'], label='Close Price', color='blue')
plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['Close'], marker='^', color='g', label='Buy Signal')
plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['Close'], marker='v', color='r', label='Sell Signal')
plt.title('Buy and Sell Signals on AMD Historical Data')
plt.xlabel('Date')
plt.ylabel('Price')
plt.legend()
plt.show()