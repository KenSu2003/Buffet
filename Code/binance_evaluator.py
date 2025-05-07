import pandas as pd
import matplotlib.pyplot as plt

# Load the Excel file
file_path = "binance_trades.xlsx"
xls = pd.ExcelFile(file_path)

# Load the data from the first sheet
df = pd.read_excel(xls, sheet_name='sheet1')

# Convert 'Date(UTC)' to datetime format
df['Date(UTC)'] = pd.to_datetime(df['Date(UTC)'])

# Sort the dataframe by date
df = df.sort_values(by='Date(UTC)')

# Plot trade prices over time
plt.figure(figsize=(12, 6))
plt.plot(df['Date(UTC)'], df['Price'], marker='o', linestyle='-', label='Trade Price')

# Highlight buy and sell trades
buy_trades = df[df['Type'] == 'BUY']
sell_trades = df[df['Type'] == 'SELL']

plt.scatter(buy_trades['Date(UTC)'], buy_trades['Price'], color='green', label='Buy Trades', marker='^', s=100)
plt.scatter(sell_trades['Date(UTC)'], sell_trades['Price'], color='red', label='Sell Trades', marker='v', s=100)

plt.xlabel('Date (UTC)')
plt.ylabel('Price (USDT)')
plt.title('Trade Price Over Time')
plt.legend()
plt.grid(True)

# Show the plot
plt.show()
