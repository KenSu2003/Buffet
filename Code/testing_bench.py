import optimizers
from testing_tools import calculate_pnl
from datetime import datetime, timedelta
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from tester import tester
from strategies import Momentum, calculate_order_size
from alpaca_api import get_open_position, get_balance

# SYMBOL = 'BTC/USD'
# CRYPTO_OR_STOCK = 'crypto'
# end_time = datetime.now()
# # start_time = end_time-timedelta(days=31)
# start_time = end_time-timedelta(days=90)
# # time_interval = TimeFrame(4,TimeFrameUnit.Hour)
# time_interval = TimeFrame(1,TimeFrameUnit.Day)
# rsi_high, rsi_low = 70, 30
# position_size, take_profit, stop_loss = 1000, 10, 2 
# rsi_weight, macd_weight, bb_weight = 1, 1, 1

# PROGRESS_LOG = False
# TRADE_LOG = True

# if PROGRESS_LOG: print("Default Parameters Set")

# ####### Setup Tester #######
# if PROGRESS_LOG: print("Setting Up Tester")
# paper_tester = tester(SYMBOL, CRYPTO_OR_STOCK, start_time, end_time, time_interval, rsi_high, rsi_low, position_size, take_profit, stop_loss)
# if PROGRESS_LOG: print("Tester Setup Complete")

# ####### Test & Analyze Strategy #######
# if PROGRESS_LOG: print("Testing Strategy")
# df = paper_tester.test()
# if PROGRESS_LOG: print("Strategy Tested")

# if PROGRESS_LOG: print("Analyzing Strategy") 
# basic_pnl, basic_roi = calculate_pnl(df, position_size, take_profit, stop_loss)
# if TRADE_LOG: print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")
# if PROGRESS_LOG: print("Strategy Analzed")

# ####### Setup Optimizer #######
# if PROGRESS_LOG: print("Setting Up Optimizer")
# optimizer = optimizers.BasicOptimizer(df, SYMBOL, start_time, end_time, time_interval)
# if PROGRESS_LOG: print("Optimizer Setup Complete")

# ####### Optimize Strategy #######
# if PROGRESS_LOG: print("Optimizing Strategy")
# optimized_parameters = optimizer.optimize()
# print(optimized_parameters)
# if PROGRESS_LOG: print(optimized_parameters)
# if PROGRESS_LOG: print("Strategy Optimized")

# ####### Test Opimized Strategy #######
# if PROGRESS_LOG: print("Testing Optimized Parameters")
# optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = optimizer.get_optimized_parameters()
# optimized_tester = tester(SYMBOL, CRYPTO_OR_STOCK, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
# optimized_df = optimized_tester.test()
# optimized_pnl, optimized_roi = calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss, )
# if TRADE_LOG: print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
# if PROGRESS_LOG: print("Optimized Testing Complete")

# ####### Determine Parameter #######
# if optimized_roi > basic_roi:
#     if TRADE_LOG: print("Excuting Trades using Optimized Parameters")
#     position_size = optimized_position_size
#     rsi_high=optimized_rsi_high
#     rsi_low=optimized_rsi_low
#     rsi_weight=optimized_rsi_weight
#     macd_weight=optimized_macd_weight
#     bb_weight=optimized_bb_weight
# else:
#     if TRADE_LOG: print("Excuting Trades using Basic Parameters")


# ####### Evaluate Signal #######
# latest_signal = Momentum(df,rsi_high,rsi_low,rsi_weight,macd_weight,bb_weight).evaluate_latest()
# print("Latest Signal",latest_signal)


####### Evaluate Order Size ########
# starting_balance = 1000000  # Initial captal
# current_account_balance = 804000 # Current account balance
# signal = -4                     # Latest signal strength
# max_position_size_percentage = 1  # Maximum position size of current account balance
# current_position_size_dollars = 100000 # Current position size in dollars
# capital_per_symbol_start = 5000  # Capital allocation per symbol

# order_size_dollars = calculate_order_size(starting_balance, current_account_balance, signal, max_position_size_percentage, current_position_size_dollars, capital_per_symbol_start)
# print(f"Order Size in Dollars: ${order_size_dollars:.2f}")


# ——————— Example usage with different capital allocations for each symbol
symbol = 'BTC/USD'
starting_balance = 100000  # Initial capital
current_account_balance = get_balance()

sym1_signal = 4.5
sym2_signal = 2.4
sym3_signal = -10.53

starting_sym1_portfolio = 1
starting_sym2_portfolio = 0.3
starting_sym3_portfolio = 0.2

# Maximum position size of account (Dynamically Adjusted from Risk-Analysis)
max_pos_size_perc_1 = 1  # Set to a reasonable value
max_pos_size_perc_2 = 0.0  # Set to a reasonable value
max_pos_size_perc_3 = 0.2  # Set to zero as mentioned

# Current position size of account
cur_pos_size_dol_1 = float(get_open_position(symbol=symbol).market_value)
cur_pos_size_dol_2 = 100
cur_pos_size_dol_3 = 3000

symbol_trade_detail = {
    'symbol1': (starting_balance * starting_sym1_portfolio, sym1_signal, max_pos_size_perc_1, cur_pos_size_dol_1),
    'symbol2': (starting_balance * starting_sym2_portfolio, sym2_signal, max_pos_size_perc_2, cur_pos_size_dol_2),
    'symbol3': (starting_balance * starting_sym3_portfolio, sym3_signal, max_pos_size_perc_3, cur_pos_size_dol_3)
}

for symbol, trade_detail in symbol_trade_detail.items():
    allocation = trade_detail[0]
    signal = trade_detail[1]
    max_position_size_percentage = trade_detail[2]
    current_position_size_dollars = trade_detail[3]

    order_size_dollars = calculate_order_size(starting_balance, current_account_balance, signal, max_position_size_percentage, current_position_size_dollars, allocation)
    print(f"Order Size for {symbol} in Dollars: ${order_size_dollars:.2f}")