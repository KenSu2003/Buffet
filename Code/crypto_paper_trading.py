from datetime import date, timedelta, datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import optimize_strategy, crypto_tools as tools
from crypto_tester import tester
from momentum_trading import Strategy as Momentum   # from strategies import Momentum
import crypto_alpaca_api as alpaca_api
import time
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Lock


# —————————————— Initialize —————————————— 

SYMBOL = 'BTC/USD'

# Initialize lock
lock = Lock()

# Initialize a flag to indicate if parameters have been updated
parameters_updated = False

# —————————————— Do Not Edit Code Below —————————————— 

def update_parameters(progress_log):

    global parameters_updated, SYMBOL,start_time,end_time,time_interval, rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight, optimized_roi, basic_roi, position_size

    with lock:

        if progress_log: print("\nUpdating Parameters ...")

        start_run_time = time.time()
        
        ####### Set Default Parameters #######
        if progress_log: print("Setting Default Parameters")

        end_time = datetime.now()
        start_time = end_time-timedelta(days=31)
        time_interval = TimeFrame(amount=1,unit=TimeFrameUnit.Hour)
        rsi_high, rsi_low = 70, 30
        position_size, take_profit, stop_loss = 1000, 10, 2 
        rsi_weight, macd_weight, bb_weight = 1, 1, 1
        if progress_log: print("Default Parameters Set")

        ####### Setup Tester #######
        if progress_log: print("Setting Up Tester")
        paper_tester = tester(SYMBOL, start_time, end_time, time_interval, rsi_high, rsi_low, position_size, take_profit, stop_loss)
        if progress_log: print("Tester Setup Complete")

        ####### Test & Analyze Strategy #######
        if progress_log: print("Testing Strategy")
        df = paper_tester.test()
        if progress_log: print("Strategy Tested")

        if progress_log: print("Analyzing Strategy")
        # paper_tester.analyze("Paper Tester: Basic Parameter")
        # tools.plot(df,"Basic Parameters")
        basic_pnl, basic_roi = tools.calculate_pnl(df, position_size, take_profit, stop_loss)
        if trade_log: print(f"Total PnL: ${basic_pnl:.2f}\t({basic_roi*100:.2f}%)")
        if progress_log: print("Strategy Analzed")

        ####### Setup Optimizer #######
        if progress_log: print("Setting Up Optimizer")
        stock_optimizer = optimize_strategy.BasicOptimization(df, SYMBOL, start_time, end_time, time_interval)
        if progress_log: print("Optimizer Setup Complete")

        ####### Optimize Strategy #######
        if progress_log: print("Optimizing Strategy")
        optimized_parameters = stock_optimizer.optimize()
        if progress_log: print(optimized_parameters)
        if progress_log: print("Strategy Optimized")

        ####### Test Opimized Strategy #######
        if progress_log: print("Testing Optimized Parameters")
        optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = stock_optimizer.get_optimized_parameters()
        optimized_tester = tester(SYMBOL, start_time, end_time, time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
        optimized_df = optimized_tester.test()
        optimized_pnl, optimized_roi = tools.calculate_pnl(optimized_df, optimized_position_size, optimized_take_profit, optimized_stop_loss, )
        if trade_log: print(f"Optimized PnL: ${optimized_pnl:.2f}\t({optimized_roi*100:.2f}%)")
        if progress_log: print("Optimized Testing Complete")

        ####### Determine Parameter #######
        if optimized_roi > basic_roi:
            if trade_log: print("Excuting Trades using Optimized Parameters")
            position_size = optimized_position_size
            rsi_high=optimized_rsi_high
            rsi_low=optimized_rsi_low
            rsi_weight=optimized_rsi_weight
            macd_weight=optimized_macd_weight
            bb_weight=optimized_bb_weight
        else:
            if trade_log: print("Excuting Trades using Basic Parameters")

        run_time = time.time() - start_run_time
        if progress_log: print(f"Run time: {run_time}\n")

        
        parameters_updated = True  # Set the flag to True after parameters are updated

def execute_trade(progress_log, trade_log):

    with lock:

        if not parameters_updated:
            print("\nParameters not updated yet, skipping trade execution.")
            return  # Exit if parameters are not updated

        if progress_log: print("\nExecuting Trades ...")
        if progress_log: print(rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight)

        ####### Evaluate Trading Signal #######
        most_recent_df = tools.setup(SYMBOL,start_time,end_time,time_interval)
        strategy = Momentum(most_recent_df, rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight)
        signal = strategy.evaluate_latest()

        if optimized_roi <= 0 and  basic_roi <= 0:
            signal = 0
            if trade_log: print("Don't Trade Signal Alerted")

        ####### Determine Order Size and Execute Order #######
        open_order = alpaca_api.get_open_position(SYMBOL)       # GETTING POSITON NOT ORDER NEED TO REEVALUATE
        order_size = abs(position_size*signal)

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
                        alpaca_api.close_position(SYMBOL)   # if its an active long order close it
                    else:
                        if trade_log: print(f"Opening Long Order {open_order_id}")
                        if trade_log: print(f"Reducing Short Position by ${order_size}")
                        alpaca_api.set_order(SYMBOL,'long',order_size)
                elif signal<0:
                    order_size = current_balance
                    if trade_log: print(f"Increasing Short Position {order_size}")
                    alpaca_api.set_order(SYMBOL,'short',order_size)
            elif open_order_side > 0:   # For Active Long Position        
                if signal<0: 
                    if order_size >= current_balance: # Close Long Position
                        order_size = current_balance
                        if trade_log: print(f"Closing Long Position {open_order_id}")
                        alpaca_api.close_position(SYMBOL)  # if its an active short order close it
                    else:
                        if trade_log: print(f"Opening Short Order {open_order_id}")
                        if trade_log: print(f"Reducing Long Position by ${abs(order_size)}")
                        alpaca_api.set_order(SYMBOL,'short',order_size)
                elif signal>0:
                    if order_size>account_balance: order_size = account_balance
                    if trade_log: print(f"Increasing Long Position {order_size}")
                    alpaca_api.set_order(SYMBOL,'long',order_size)
            else:
                print("No new trades made.\n")
        else:
            if signal > 0:
                if trade_log: print(f"Opening a new Long ${order_size} Order")
                alpaca_api.set_order(SYMBOL,'long',order_size)
            elif signal < 0:
                if trade_log: print("Insufficient Fund.\n")
            else:
                if trade_log: print("No trades made.\n")

    ''' 
    Should reconsider renaming position_size to order_size
    '''

    

# —————————————— Do Not Edit Code Above —————————————— 



# —————————————— Testing Console —————————————— 

progress_log = True
trade_log = True

# Create a lock object
# lock = Lock()

# Set up the initial parameters
update_parameters(progress_log) 

# Create an instance of the scheduler
scheduler = BlockingScheduler()

# Update Parameters Every HOUR
scheduler.add_job(update_parameters, 'interval', hours=1, args=[progress_log])
print("Paramters updating every 1 minutes")

# Calculate Signal and Excute Trade Every 15 MINUTES (USE 1 MINUTE FORE TESTING
scheduler.add_job(execute_trade, 'interval', minutes=15, args=[progress_log, trade_log])
print("Trades Excuted every 1 minutes")

try:
    print("Starting the scheduler...")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")



