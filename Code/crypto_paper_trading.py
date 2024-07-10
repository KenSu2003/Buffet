from datetime import date, timedelta, datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import optimize_strategy, crypto_tools as tools
from crypto_tester import tester
from momentum_trading import Strategy as Momentum   # from strategies import Momentum
import crypto_alpaca_api as alpaca_api


# —————————————— Testing Console —————————————— 

progress_log = False
trade_log = True

# —————————————— Do Not Edit Code Below —————————————— 

####### Set Default Parameters #######
if progress_log: print("Setting Default Parameters")
symbol = 'BTC/USD'
end_time = datetime.now()
start_time = end_time-timedelta(days=31)
time_interval = time_interval = TimeFrame(amount=1,unit=TimeFrameUnit.Hour)
RSI_HIGH, RSI_LOW = 70, 30
POSITION_SIZE, TAKE_PROFIT, STOP_LOSS = 1000, 10, 2 
RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT = 1, 1, 1
if progress_log: print("Default Parameters Set")

####### Setup Tester #######
if progress_log: print("Setting Up Tester")
paper_tester = tester(symbol, start_time, end_time, time_interval, RSI_HIGH, RSI_LOW, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
if progress_log: print("Tester Setup Complete")

####### Test & Analyze Strategy #######
if progress_log: print("Testing Strategy")
df = paper_tester.test()
if progress_log: print("Strategy Tested")

if progress_log: print("Analyzing Strategy")
# paper_tester.analyze("Paper Tester: Basic Parameter")
# tools.plot(df,"Basic Parameters")
basic_pnl, basic_roi = tools.calculate_pnl(df, POSITION_SIZE, TAKE_PROFIT, STOP_LOSS)
if trade_log: print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")
if progress_log: print("Strategy Analzed")

####### Setup Optimizer #######
if progress_log: print("Setting Up Optimizer")
stock_optimizer = optimize_strategy.BasicOptimization(df, symbol, start_time, end_time, time_interval)
if progress_log: print("Optimizer Setup Complete")

####### Optimize Strategy #######
if progress_log: print("Optimizing Strategy")
optimized_parameters = stock_optimizer.optimize()
if progress_log: print(optimized_parameters)
if progress_log: print("Strategy Optimized")

####### Test Opimized Strategy #######
if progress_log: print("Testing Optimized Parameters")
optimized_POSITION_SIZE, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT = stock_optimizer.get_optimized_parameters()
optimized_tester = tester(symbol, start_time, end_time, time_interval, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT)
optimized_df = optimized_tester.test()
optimized_pnl, optimized_roi = tools.calculate_pnl(optimized_df, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, )
if trade_log: print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
if progress_log: print("Optimized Testing Complete")

####### Determine Parameter #######
if optimized_roi < 0 and  basic_roi < 0:
    signal = 0
elif optimized_roi > basic_roi:
    if trade_log: print("Excuting Trades using Optimized Parameters")
    POSITION_SIZE = optimized_POSITION_SIZE
    RSI_HIGH=optimized_RSI_HIGH
    RSI_LOW=optimized_RSI_LOW
    RSI_WEIGHT=optimized_RSI_WEIGHT
    MACD_WEIGHT=optimized_MACD_WEIGHT
    BB_WEIGHT=optimized_BB_WEIGHT
else:
    if trade_log: print("Excuting Trades using Basic Parameters")

####### Evaluate Trading Signal #######
most_recent_df = tools.setup(symbol,start_time,end_time,time_interval)
strategy = Momentum(most_recent_df, RSI_HIGH, RSI_LOW, RSI_WEIGHT, MACD_WEIGHT, BB_WEIGHT)
signal = strategy.evaluate_latest()

####### Determine Order Size and Execute Order #######
open_order = alpaca_api.get_open_position(symbol)       # GETTING POSITON NOT ORDER NEED TO REEVALUATE
order_size = abs(POSITION_SIZE*signal)

# Check if there is an Active (Open) Order
if open_order != None:
    open_order_id = open_order.asset_id
    open_order_side = alpaca_api.get_buy_sell(open_order)

    current_balance = float(open_order.qty)*float(open_order.market_value)    # order size = availabe asset
    account_balance = alpaca_api.get_balance()     # order size = entire account availabe USD balance

    if open_order_side < 0: # For Active Short Position
        
        if signal>0: 
            if order_size >= account_balance: # Close Long Position
                order_size = account_balance
                if trade_log: print(f"Reducing Order Size to {order_size}.")
                if trade_log: print(f"Closing Short Position {open_order_id}")
                alpaca_api.close_position(symbol)   # if its an active long order close it
            else:
                if trade_log: print(f"Opening Long Order {open_order_id}")
                if trade_log: print(f"Reducing Short Position by ${order_size}")
                alpaca_api.set_order(symbol,'long',order_size)
        elif signal<0:
            order_size = current_balance
            if trade_log: print(f"Increasing Short Position {order_size}")
            alpaca_api.set_order(symbol,'short',order_size)
    elif open_order_side > 0:   # For Active Long Position        
        if signal<0: 
            if order_size >= current_balance: # Close Long Position
                order_size = current_balance
                if trade_log: print(f"Closing Long Position {open_order_id}")
                alpaca_api.close_position(symbol)  # if its an active short order close it
            else:
                if trade_log: print(f"Opening Short Order {open_order_id}")
                if trade_log: print(f"Reducing Long Position by ${abs(order_size)}")
                alpaca_api.set_order(symbol,'short',order_size)
        elif signal>0:
            if order_size>account_balance: order_size = account_balance
            if trade_log: print(f"Increasing Long Position {order_size}")
            alpaca_api.set_order(symbol,'long',order_size)
else:
    if signal > 0:
        if trade_log: print(f"Opening a new Long ${order_size} Order")
        alpaca_api.set_order(symbol,'long',order_size)
    elif signal < 0:
        if trade_log: print("Insufficient Fund.")
    else:
        if trade_log: print("No trades made.")

# —————————————— Do Not Edit Code Above —————————————— 

''' 
Should reconsider renaming position_size to order_size
'''