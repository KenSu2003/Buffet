import yfinance as yf
import pandas as pd
import numpy as np
import talib
import matplotlib.pyplot as plt
import csv

import strategy_tools, strategy1

# —————————————————————— Parameters ——————————————————————

# Stock
symbol = 'AMD'

# Time (time-period, time-interval)
start_date = '2023-01-01'   # default = 2023-01-01 , profit: 622.77
end_date = '2023-12-31'     # default = 2023-12-31
time_interval = '1d'

# Indicatiors
RSI_HIGH = 70
RSI_LOW = 30
POSITION_SIZE = 1000    #in USD
TAKE_PROFIT = 5         # in %  (default)5%: +$683.67, 10%: +$277.29
STOP_LOSS = 2           # in %  (default)2%: +$683.67, 1%: +$602.70, 5%: +$136.19

''' Need to test long-term and short-term ROI'''

# —————————————————————— Step 1: Fetch df ——————————————————————
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

# Calculate profitability
profit = strategy_tools.calculate_profitability(df, profit_target_pct=TAKE_PROFIT, stop_loss_pct=STOP_LOSS, trade_size=POSITION_SIZE)
print(f"Total Profit: ${profit:.2f}")

# Save data to csv file
df.to_csv('technical_indicators.csv')       # export to CSV to analyze the data more easily

# Plot the trade signals
strategy_tools.plot(plt,df)