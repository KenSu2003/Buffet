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

# —————————————————————— Step 1: Fetch data ——————————————————————

df = strategy_tools.setup(symbol, start_date, end_date, time_interval)

# —————————————————————— Step 2: Implement Strategy ——————————————————————

# Deterimine BUY/SELL signal
df = strategy1.trade(df, RSI_HIGH, RSI_LOW)

# ——————————————————————— Step 4: Analysis ——————————————————————— #

# Calculate profitability
profit = strategy_tools.calculate_profitability(df, profit_target_pct=TAKE_PROFIT, stop_loss_pct=STOP_LOSS, trade_size=POSITION_SIZE)
print(f"Total Profit: ${profit:.2f}")

# Save data to csv file
df.to_csv('technical_indicators.csv')       # export to CSV to analyze the data more easily

# Plot the trade signals
strategy_tools.plot(plt,df)