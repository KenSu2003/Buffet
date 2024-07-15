import alpaca_api
from time import time
from datetime import timedelta, datetime
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from testing_tools import setup, calculate_pnl
from tester import tester
from strategies import Momentum
from optimizers import BasicOptimizer
from apscheduler.schedulers.blocking import BlockingScheduler
from threading import Lock

# —————————————— Initialize —————————————— 

SYMBOL = 'BTC/USD'
CRYPTO_OR_STOCK = 'crypto'

# SYMBOL = 'AMD'
# CRYPTO_OR_STOCK = 'stock'

# Initialize lock
lock = Lock()

# Initialize a flag to indicate if parameters have been updated
parameters_updated = False

# —————————————— Do Not Edit Code Below —————————————— 

def update_parameters(PROGRESS_LOG):

    global parameters_updated, SYMBOL,start_time,end_time,time_interval, rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight, optimized_roi, basic_roi, position_size

    with lock:

        if PROGRESS_LOG: print("\nUpdating Parameters ...")

        start_run_time = time()
        
        ####### Set Default Parameters #######
        if PROGRESS_LOG: print("Setting Default Parameters")

        end_time = datetime.now()
        start_time = end_time-timedelta(days=31)
        time_interval = TimeFrame(amount=1,unit=TimeFrameUnit.Hour)
        rsi_high, rsi_low = 70, 30
        position_size, take_profit, stop_loss = 1000, 10, 2 
        rsi_weight, macd_weight, bb_weight = 1, 1, 1
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
        optimizer = BasicOptimizer(df, SYMBOL, start_time, end_time, time_interval)
        if PROGRESS_LOG: print("Optimizer Setup Complete")

        ####### Optimize Strategy #######
        if PROGRESS_LOG: print("Optimizing Strategy")
        optimized_parameters = optimizer.optimize()
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

        run_time = time() - start_run_time
        if PROGRESS_LOG: print(f"Run time: {run_time}\n")

        
        parameters_updated = True  # Set the flag to True after parameters are updated

def execute_trade(PROGRESS_LOG, TRADE_LOG):

    with lock:

        if not parameters_updated:
            print("\nParameters not updated yet, skipping trade execution.")
            return  # Exit if parameters are not updated

        if PROGRESS_LOG: print("\nExecuting Trades ...")
        if PROGRESS_LOG: print(rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight, position_size)

        ####### Evaluate Trading Signal #######
        most_recent_df = setup(SYMBOL,CRYPTO_OR_STOCK,start_time,end_time,time_interval)
        strategy = Momentum(most_recent_df, rsi_high, rsi_low, rsi_weight, macd_weight, bb_weight)
        signal = strategy.evaluate_latest()

        if optimized_roi <= 0 and  basic_roi <= 0:
            signal = 0
            if TRADE_LOG: print("Don't Trade Signal Alerted")

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
                        if TRADE_LOG: print(f"Reducing Order Size to {order_size}.")
                        if TRADE_LOG: print(f"Closing Short Position {open_order_id}")
                        alpaca_api.close_position(SYMBOL)   # if its an active long order close it
                    else:
                        if TRADE_LOG: print(f"Opening Long Order {open_order_id}")
                        if TRADE_LOG: print(f"Reducing Short Position by ${order_size}")
                        alpaca_api.set_order(SYMBOL,CRYPTO_OR_STOCK,'long',order_size)
                elif signal<0:
                    order_size = current_balance
                    if TRADE_LOG: print(f"Increasing Short Position {order_size}")
                    alpaca_api.set_order(SYMBOL,CRYPTO_OR_STOCK,'short',order_size)
            elif open_order_side > 0:   # For Active Long Position        
                if signal<0: 
                    if order_size >= current_balance: # Close Long Position
                        order_size = current_balance
                        if TRADE_LOG: print(f"Closing Long Position {open_order_id}")
                        alpaca_api.close_position(SYMBOL)  # if its an active short order close it
                    else:
                        if TRADE_LOG: print(f"Opening Short Order {open_order_id}")
                        if TRADE_LOG: print(f"Reducing Long Position by ${abs(order_size)}")
                        alpaca_api.set_order(SYMBOL,CRYPTO_OR_STOCK,'short',order_size)
                elif signal>0:
                    if order_size>account_balance: order_size = account_balance
                    if TRADE_LOG: print(f"Increasing Long Position {order_size}")
                    alpaca_api.set_order(SYMBOL,CRYPTO_OR_STOCK,'long',order_size)
            else:
                print("No new trades made.\n")
        else:
            if signal > 0:
                if TRADE_LOG: print(f"Opening a new Long ${order_size} Order")
                alpaca_api.set_order(SYMBOL,CRYPTO_OR_STOCK,'long',order_size)
            elif signal < 0:
                if TRADE_LOG: print("Insufficient Fund.\n")
            else:
                if TRADE_LOG: print("No trades made.\n")

    ''' 
    Should reconsider renaming position_size to order_size
    '''
# —————————————— Do Not Edit Code Above —————————————— 



# —————————————— Testing Console —————————————— 

PROGRESS_LOG = False
TRADE_LOG = True

# Create a lock object
# lock = Lock()

# Set up the initial parameters
update_parameters(PROGRESS_LOG) 

# Create an instance of the scheduler
scheduler = BlockingScheduler()

# Update Parameters Every HOUR
# scheduler.add_job(update_parameters, 'interval', hours=1, args=[PROGRESS_LOG])
# print("Paramters updating every 1 hour")
scheduler.add_job(update_parameters, 'interval', minutes=2, args=[PROGRESS_LOG])

# Calculate Signal and Excute Trade Every 15 MINUTES (USE 1 MINUTE FORE TESTING
# scheduler.add_job(execute_trade, 'interval', minutes=15, args=[PROGRESS_LOG, TRADE_LOG])
# print("Trades Excuted every 15 minutes")
scheduler.add_job(execute_trade, 'interval', minutes=1, args=[PROGRESS_LOG, TRADE_LOG])


try:
    print("Starting the scheduler...")
    scheduler.start()
except (KeyboardInterrupt, SystemExit):
    print("Scheduler stopped.")