from datetime import date, timedelta, datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import optimize_strategy, strategy_tools as tools
from stock_tester import tester
from momentum_trading import Strategy as Momentum   # from strategies import Momentum

# —————————————— Set Parameters —————————————— 

print("Setting Default Parameters")
symbol = 'AMD'
end_time = datetime.now()


start_time = end_time-timedelta(days=31)
time_interval = time_interval = TimeFrame(amount=1,unit=TimeFrameUnit.Hour)

RSI_HIGH, RSI_LOW = 70, 30
POSITION_SIZE, TAKE_PROFIT, STOP_LOSS = 1000, 10, 2 
print("Default Parameters Set")



# —————————————— Do Not Edit Code Below —————————————— 

####### Setup Tester #######
print("Setting Up Tester")
paper_tester = tester(symbol, start_time, end_time, time_interval, RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
print("Tester Setup Completed")

####### Test & Analyze Strategy #######
print("Testing Strategy")
df = paper_tester.test()
print("Strategy Tested")

print("Analyzing Strategy")
# paper_tester.analyze("Paper Tester: Basic Parameter")
# tools.plot(df,"Basic Parameters")
basic_pnl, basic_roi = tools.calculate_pnl(df, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")

####### Setup Optimizer #######
print("Setting Up Optimizer")
stock_optimizer = optimize_strategy.BasicOptimization(df, symbol, start_time, end_time, time_interval)
print("Optimizer Setup Complete")

####### Optimize Strategy #######
print("Optimizing Strategy")
optimized_parameters = stock_optimizer.optimize()
print(optimized_parameters)
print("Strategy Optimized")

####### Test Opimized Strategy #######
print("Testing Optimized Parameters")
optimized_POSITION_SIZE, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT = stock_optimizer.get_optimized_parameters()
optimized_tester = tester(symbol, start_time, end_time, time_interval, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT)
optimized_df = optimized_tester.test()
optimized_pnl, optimized_roi = tools.calculate_pnl(optimized_df, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, )
print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
print("Optimized Testing Complete")

''' 
Need to inspect on why take-profit is so low. 
I think it's becuase it's high frequency trading.
'''

####### Determine Parameter #######
if optimized_roi > basic_roi:
    print("Excuting Trades using Optimized Parameters")
    POSITION_SIZE = optimized_POSITION_SIZE
    RSI_HIGH=optimized_RSI_HIGH
    RSI_LOW=optimized_RSI_LOW
    RSI_WEIGHT=optimized_RSI_WEIGHT
    MACD_WEIGHT=optimized_MACD_WEIGHT
    BB_WEIGHT=optimized_BB_WEIGHT
else:
    print("Excuting Trades using Basic Parameters")

####### Evaluate Trading Signal #######
most_recent_df = tools.setup(symbol,start_time,end_time,time_interval)
strategy = Momentum(most_recent_df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)
signal = strategy.evaluate_latest()


order_size = POSITION_SIZE*signal

####### Excute Order #######
if signal>=1:
    print(f"Buy {order_size}")
    # alpacaAPI.buy
elif signal<=-1:
    print(f"Sell {order_size}")
    # alpacaAPI.sell
