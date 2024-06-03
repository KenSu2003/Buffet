'''
Look at the data from past year from current day and make a trading decision.
'''

import strategy_testing, strategy_tools, momentum_trading
from optimize_strategy import optimization
from datetime import date, timedelta

year = 2023
trade_date = date(year,1,1)
data_end_date = trade_date-timedelta(1)
data_start_date = data_end_date-timedelta(365)
symbol = 'AMD'
time_interval = '1d'

t = strategy_testing.tester(symbol, data_start_date, data_end_date, time_interval, 70, 30, 1000, 5, 2)
df = t.test()
momentum_trading.trade(df)
graph_title = f"Before Optimization {year}"
t.analyze(df, graph_title)

optimizer = optimization('AMD', '2020-01-01', '2020-12-31', '1d').optimize()
optimized_POSITION_SIZE = optimizer.max['params'].get('POSITION_SIZE')
optimized_RSI_HIGH = optimizer.max['params'].get('RSI_HIGH')
optimized_RSI_LOW = optimizer.max['params'].get('RSI_LOW')
optimized_STOP_LOSS = optimizer.max['params'].get('STOP_LOSS')
optimized_TAKE_PROFIT = optimizer.max['params'].get('TAKE_PROFIT')
optimized_roi = momentum_trading.trade(df,optimized_RSI_HIGH,optimized_RSI_LOW)
pnl, roi = strategy_tools.calculate_pnl(df, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_POSITION_SIZE)

o = strategy_testing.tester(symbol, data_start_date, data_end_date, time_interval, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS)
graph_title = f"After Optimization {year}"
t.analyze(df, graph_title)
print("After Optimization ROI =", roi)