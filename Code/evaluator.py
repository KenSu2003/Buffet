from alpaca_api import *
from testing_tools import *
import datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit

SIDE_INDEX = 22
ORDER_FILLED_TIME = 5

symbol = 'BTC/USD'
start_time = datetime.date(2024,8,1)
end_time = datetime.date.today()
interval = TimeFrame(amount=15,unit=TimeFrameUnit.Minute)

barset = setup(symbol,'crypto',start_time,end_time,interval)
barset.to_csv('./Data/AlpacaHistoricalData.csv')

orders = get_all_orders(symbol)
order_sides = [orders[SIDE_INDEX][order][1] for order in range(len(orders[SIDE_INDEX]))]
order_times = [orders[ORDER_FILLED_TIME][order][1] for order in range(len(orders[ORDER_FILLED_TIME]))]

filled_orders = {'order_time':order_times,'order_side':order_sides}
filled_orders = pd.DataFrame(filled_orders)
filled_orders['order_time'] = pd.to_datetime(filled_orders['order_time']).dt.round('15min')
filled_orders.set_index('order_time', inplace=True)

merged_data = barset.merge(filled_orders, left_index=True, right_index=True, how='left')
merged_data.to_csv('./Data/AlpacaDataset.csv')


# Plot the barset data
plt.figure(figsize=(42, 21))
plt.plot(merged_data.index, merged_data['close'], label='Barset Data')

# Overlay the 'buy' and 'sell' orders
buy_orders = merged_data[merged_data['order_side'] == 'buy']
sell_orders = merged_data[merged_data['order_side'] == 'sell']

plt.scatter(buy_orders.index, buy_orders['close'], color='green', marker='^', label='Buy Orders')
plt.scatter(sell_orders.index, sell_orders['close'], color='red', marker='v', label='Sell Orders')

# Add labels and legend
plt.xlabel('Time')
plt.ylabel('Value')
plt.title('Barset Data with Buy and Sell Orders')
plt.legend()

# Show the plot
plt.show()