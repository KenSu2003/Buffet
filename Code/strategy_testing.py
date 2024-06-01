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
start_date = '2022-01-01'   # default = 2023-01-01 , profit: 622.77
end_date = '2022-12-31'     # default = 2023-12-31
time_interval = '1d'

# Indicators
RSI_HIGH = 77
RSI_LOW = 32
POSITION_SIZE = 1990
TAKE_PROFIT = 5         
STOP_LOSS = 4

# Need to test long-term and short-term ROI

# IMPORTANT
# apparently RSIx2+BBx1 = +$683.67 and RSIx1,MACDx1,BBx1 = $617.56
RSI_WEIGHT = 1
MACD_WEIGHT = 1
BB_WEIGHT = 1


# fetch data
df = strategy_tools.setup(symbol, start_date, end_date, time_interval)              

# implement strategy, determine BUY/SELL signal
df = strategy1.trade(df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)     

# Calculate profitability
profit = strategy_tools.calculate_pnl(df, profit_target_pct=TAKE_PROFIT, stop_loss_pct=STOP_LOSS, trade_size=POSITION_SIZE)
print(f"Total Profit: ${profit:.2f}")

# Save data to csv file
df.to_csv('technical_indicators.csv')       # export to CSV to analyze the data more easily

# Plot the trade signals
strategy_tools.plot(plt, df)

# Save year and PnL to CSV file
with open('pnl_record.csv', mode='a', newline='') as file:
    writer = csv.writer(file)
    year = f"{start_date[:4]}-{end_date[:4]}"
    writer.writerow([year, profit])