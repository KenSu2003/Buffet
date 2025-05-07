import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import savgol_filter
from testing_tools import setup
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit



SYMBOL = 'BTC/USD'
CRYPTO_OR_STOCK = 'crypto'
# SYMBOL = 'MGC'
# CRYPTO_OR_STOCK = 'stock'
# end_time = datetime.now()
end_time = datetime(2024,2,3)
# start_time = end_time-timedelta(days=31)
start_time = end_time-timedelta(days=365*5)
time_interval = TimeFrame(4,TimeFrameUnit.Hour)
# time_interval = TimeFrame(1,TimeFrameUnit.Day)
rsi_high, rsi_low = 70, 30
position_size, take_profit, stop_loss = 1000, 10, 2 
rsi_weight, macd_weight, bb_weight = 1, 1, 1


# Load the dataset
# file_path = "Data/AlpacaHistoricalData.csv"  # Update the file path if necessary
# df = pd.read_csv(file_path)
df = setup(SYMBOL, CRYPTO_OR_STOCK, start_time, end_time, time_interval)

# Debugging: Print column names
print("Columns in DataFrame:", df.columns)

# Ensure timestamp is present
if 'timestamp' not in df.columns:
    print("Timestamp column missing. Checking index...")
    df.reset_index(inplace=True)  # Convert index to column if needed

# Convert timestamp to datetime format
df['timestamp'] = pd.to_datetime(df['timestamp'], errors='coerce')

# Sort data
df = df.sort_values(by='timestamp')

# Check if timestamps are properly converted
if df['timestamp'].isnull().all():
    raise ValueError("Error: Timestamp conversion failed. Check API response format.")

# Continue with Savitzky-Golay filtering...


# Sort data by timestamp in case it's unordered
df = df.sort_values(by='timestamp')

# Extract closing prices
x = np.arange(len(df))  # Index as x-axis
y = df['close'].values  # Closing prices

# Apply Savitzky-Golay filter for smoothing
window_size = 11  # Must be an odd number
poly_order = 3  # Polynomial order
y_smoothed = savgol_filter(y, window_size, poly_order)

# Plot original and smoothed data
plt.figure(figsize=(12, 6))
plt.plot(df['timestamp'], y, label='Original Close Price', linestyle='dashed', alpha=0.6)
plt.plot(df['timestamp'], y_smoothed, label='Smoothed Close Price (Savitzky-Golay)', linewidth=2)
plt.xlabel("Time")
plt.ylabel("Close Price")
plt.title("Savitzky-Golay Filter Applied to Closing Prices")
plt.legend()
plt.xticks(rotation=45)
plt.grid()
plt.show()
