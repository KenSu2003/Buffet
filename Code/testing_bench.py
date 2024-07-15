import optimizers
import testing_tools as tools
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from tester import tester

SYMBOL = 'BTC/USD'
crypto_or_stock = 'crypto'
end_time = datetime.now()
start_time = end_time-timedelta(days=31)
time_interval = TimeFrame(4,TimeFrameUnit.Hour)
rsi_high, rsi_low = 70, 30
position_size, take_profit, stop_loss = 1000, 10, 2 
rsi_weight, macd_weight, bb_weight = 1, 1, 1

progress_log = False
trade_log = True

if progress_log: print("Default Parameters Set")

####### Setup Tester #######
if progress_log: print("Setting Up Tester")
paper_tester = tester(SYMBOL, crypto_or_stock, start_time, end_time, time_interval, rsi_high, rsi_low, position_size, take_profit, stop_loss)
if progress_log: print("Tester Setup Complete")

####### Test & Analyze Strategy #######
if progress_log: print("Testing Strategy")
df = paper_tester.test()
if progress_log: print("Strategy Tested")

if progress_log: print("Analyzing Strategy") 
basic_pnl, basic_roi = tools.calculate_pnl(df, position_size, take_profit, stop_loss)
if trade_log: print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")
if progress_log: print("Strategy Analzed")

####### Setup Optimizer #######
if progress_log: print("Setting Up Optimizer")
optimizer = optimizers.BasicOptimizer(df, SYMBOL, start_time, end_time, time_interval)
if progress_log: print("Optimizer Setup Complete")

####### Optimize Strategy #######
if progress_log: print("Optimizing Strategy")
optimized_parameters = optimizer.optimize()
print(optimized_parameters)
if progress_log: print(optimized_parameters)
if progress_log: print("Strategy Optimized")

####### Test Opimized Strategy #######
if progress_log: print("Testing Optimized Parameters")
optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = optimizer.get_optimized_parameters()
optimized_tester = tester(SYMBOL, crypto_or_stock, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
optimized_df = optimized_tester.test()
optimized_pnl, optimized_roi = tools.calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss, )
if trade_log: print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
if progress_log: print("Optimized Testing Complete")