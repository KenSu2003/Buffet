import optimizers
from testing_tools import simulate_trades, calculate_pnl
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from tester import tester
from strategies import Momentum

SYMBOL = 'BTC/USD'
CRYPTO_OR_STOCK = 'crypto'
end_time = datetime.now()
start_time = end_time-timedelta(days=31)
time_interval = TimeFrame(4,TimeFrameUnit.Hour)
rsi_high, rsi_low = 70, 30
position_size, take_profit, stop_loss = 1000, 10, 2 
rsi_weight, macd_weight, bb_weight = 1, 1, 1

PROGRESS_LOG = True
TRADE_LOG = True

if PROGRESS_LOG: print("Default Parameters Set")

####### Setup Tester #######
if PROGRESS_LOG: print("Setting Up Tester")
paper_tester = tester(SYMBOL, CRYPTO_OR_STOCK, start_time, end_time, time_interval, rsi_high, rsi_low, position_size, take_profit, stop_loss)
if PROGRESS_LOG: print("Tester Setup Complete")

####### Test & Analyze Strategy #######
if PROGRESS_LOG: print("Testing Strategy")
df = paper_tester.test()
if PROGRESS_LOG: print("Strategy Tested")

if PROGRESS_LOG: print("Analyzing Strategy") 
basic_pnl, basic_roi = calculate_pnl(df, position_size, take_profit, stop_loss)
if TRADE_LOG: print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")
if PROGRESS_LOG: print("Strategy Analzed")

####### Setup Optimizer #######
if PROGRESS_LOG: print("Setting Up Optimizer")
optimizer = optimizers.BasicOptimizer(df, SYMBOL, start_time, end_time, time_interval)
if PROGRESS_LOG: print("Optimizer Setup Complete")

####### Optimize Strategy #######
if PROGRESS_LOG: print("Optimizing Strategy")
optimized_parameters = optimizer.optimize()
print(optimized_parameters)
if PROGRESS_LOG: print(optimized_parameters)
if PROGRESS_LOG: print("Strategy Optimized")

####### Test Opimized Strategy #######
if PROGRESS_LOG: print("Testing Optimized Parameters")
optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = optimizer.get_optimized_parameters()
optimized_tester = tester(SYMBOL, CRYPTO_OR_STOCK, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
optimized_df = optimized_tester.test()
optimized_pnl, optimized_roi = calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss, )
if TRADE_LOG: print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
if PROGRESS_LOG: print("Optimized Testing Complete")

####### Determine Parameter #######
if optimized_roi > basic_roi:
    if TRADE_LOG: print("Excuting Trades using Optimized Parameters")
    position_size = optimized_position_size
    rsi_high=optimized_rsi_high
    rsi_low=optimized_rsi_low
    rsi_weight=optimized_rsi_weight
    macd_weight=optimized_macd_weight
    bb_weight=optimized_bb_weight
else:
    if TRADE_LOG: print("Excuting Trades using Basic Parameters")


####### Evaluate Signal #######
latest_signal = Momentum(df,rsi_high,rsi_low,rsi_weight,macd_weight,bb_weight).evaluate_latest()
print("Latest Signal",latest_signal)
