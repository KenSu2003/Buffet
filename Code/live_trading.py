from datetime import date, timedelta, datetime
from alpaca.data.timeframe import TimeFrame
import stock_tester, optimize_strategy, strategy_tools as tools

####### Set Parameters #######
print("Setting Default Parameters")
symbol = 'AMD'
end_date = datetime.now()
start_date = end_date-timedelta(days=365)
time_interval = TimeFrame.Day
RSI_HIGH, RSI_LOW = 70, 30
POSITION_SIZE, TAKE_PROFIT, STOP_LOSS = 1000, 5, 2 
print("Default Parameters Set")

####### Setup Tester #######
print("Setting Up Tester")
live_tester = stock_tester.tester(symbol, start_date, end_date, time_interval, RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
print("Tester Setup Completed")

####### Test & Analyze Strategy #######
print("Testing Strategy")
df = live_tester.test()
print("Strategy Tested")

print("Analyzing Strategy")
basic_pnl, basic_roi = tools.calculate_pnl(df, TAKE_PROFIT, STOP_LOSS, POSITION_SIZE)
print("Basic ROI = %.2f%%"%(basic_roi*100))

####### Setup Optimizer #######
print("Setting Up Optimizer")
stock_optimizer = optimize_strategy.BasicOptimization(df, symbol, start_date, end_date, time_interval)
print("Optimizer Setup Completed")

####### Optimize Strategy #######
print("Optimizing Strategy")
optimized_parameters = stock_optimizer.optimize()
print(optimized_parameters)
print("Strategy Optimized")

####### Test Opimized Strategy #######
print("Testing Optimized Parameters")
optimized_POSITION_SIZE, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT = stock_optimizer.get_optimized_parameters()
optimized_tester = stock_tester.tester(symbol, start_date, end_date, time_interval, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT)
optimized_df = optimized_tester.test()
optimized_pnl, optimized_roi = tools.calculate_pnl(optimized_df, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_POSITION_SIZE)
print("Optimized ROI = %.2f%%"%(optimized_roi*100))
print("Optimized Testing Complete")


####### Determine Parameter #######
# if optimized_roi > basic_roi:
#     alpacaAPI.execute_trade(optimized_parameters) 
# else:
#     alpacaAPI.execute_trade(parameters) 
