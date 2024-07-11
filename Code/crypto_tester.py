import crypto_tools as tools
import momentum_trading as strategy
from datetime import timedelta, datetime
from optimize_strategy import BasicOptimization
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
import csv, os

class tester:

    def __init__(self, 
                 symbol, 
                 start_date, end_date, time_interval,       
                 rsi_high, rsi_low,
                 position_size, take_profit, stop_loss,
                 rsi_weight=1, macd_weight=1, bb_weight=1):

        self.symbol = symbol

        # Time (time-period, time-interval)
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

        # Technical Indicators
        self.rsi_high = rsi_high
        self.rsi_low = rsi_low
        self.position_size = position_size          # number of stocks not $
        self.take_profit = take_profit              # in % not .
        self.stop_loss = stop_loss                  # in % not .

        self.rsi_weight = rsi_weight
        self.macd_weight = macd_weight
        self.bb_weight = bb_weight

        # print("Setting up Alpaca Datafile")
        self.df = tools.setup(self.symbol, self.start_date, self.end_date, self.time_interval)  # fetch data

    
    def test(self):
        
        # print("Testing Strategy")
        strategy1 = strategy.Strategy(self.df)
        strategy1.evaluate_indicators()
        df = self.simulate_all_trades()    # implement strategy, determine BUY/SELL signal    
        self.df = df
        # print("Strategy Tested")
        
        return df
    
    def calculate_pnl(self):
        return tools.calculate_pnl(self.df, self.position_size, self.take_profit, self.stop_loss)
    
    def simulate_all_trades(self):
        """
        Simulate all the trades in the given time frame based on the given parameter using this strategy.
        """

        self.df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
        for i in range(len(self.df)):
            # Calculate the new signal value directly
            signal_value = self.df.at[self.df.index[i], 'RSI_signal']*self.rsi_weight + self.df.at[self.df.index[i], 'MACD_signal']*self.macd_weight + self.df.at[self.df.index[i], 'BB_diverging']*self.bb_weight
            self.df.at[self.df.index[i], 'Signal'] = float(signal_value)  # float (not int) makes it more accurate
        return self.df

    def analyze(self, title):

        # print("Analyzing Data")
        
        file_path = "./crypto_data"

        # Calculate PNL
        pnl, roi = tools.calculate_pnl(self.df, self.position_size, self.take_profit, self.stop_loss) 
        print(f"Total PnL: ${pnl:.2f}\t({roi*100:.2f}%)")
        year = f"{self.start_date.year}-{self.end_date.year}"

        # Save the Technical Indicator Datafile
        # print("Saving Datafile")
        filename = f"{file_path}/TI_{self.symbol}_{year}_{self.time_interval}.csv"

        # Ensure the directory for the filename exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        self.df.to_csv(filename)       # Save data to csv file, export to CSV to analyze the data more easily  
        # print("Datafile Saved")

        # Save year and PnL to CSV file
        file_name = f"{file_path}/pnl_record_{title}.csv"

        # Ensure the directory for the PnL record exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([year, pnl])
        # print("Data Analyzed")

        # Plot the trades
        graph_title = f"{file_path}/{title}"

        # Ensure the directory for the graph_title record exists
        os.makedirs(os.path.dirname(graph_title), exist_ok=True)

        tools.plot(self.df, graph_title)    
        
# ——————————————————- Run Tests ————————————————————

# # Default Parameters
# symbol = 'BTC/USDT'
# year = datetime.now().year

# # end_time = datetime.now()
# # start_time = end_time-timedelta(days=31)
# # time_interval = TimeFrame(amount=1,unit=TimeFrameUnit.Hour)

# end_time = datetime(2024,3,12)
# # start_date = end_date-timedelta(days=1)
# start_time = datetime(2024,3,1)
# # time_interval = TimeFrame.Minute
# time_interval = TimeFrame(amount=4,unit=TimeFrameUnit.Hour)

# rsi_high, rsi_low = 70, 30
# position_size, take_profit, stop_loss = 1000, 5, 2 
# print("Default Parameters Set")

# ####### Basic Testing #######
# print("Testing Default Strategy")
# t = tester(symbol,start_time,end_time,time_interval,rsi_high,rsi_low,position_size,take_profit,stop_loss)
# t.test()
# graph_title = f"{symbol} - {year} {time_interval}"
# t.analyze(graph_title)


# ####### Test Different Years #######
# # years = [2019, 2020, 2021, 2022, 2023]
# # for year in range (2019,2024):
# #     start_date = date(year,1,1)
# #     end_date = date(year,12,31)
# #     years_test = tester(symbol,start_date,end_date,time_interval,rsi_high,rsi_low,position_size,take_profit,stop_loss)
# #     df = years_test.test()
# #     graph_title = f"PnL in {year}"
# #     years_test.analyze(df, graph_title)

# ####### Test Different Intervals #######
# # intervals = ['1d','5d','1wk','1mo','3mo']
# # for interval in intervals:
# #     interval_test = tester(symbol,start_date,end_date,interval,rsi_high,rsi_low,position_size,take_profit,stop_loss)
# #     df = interval_test.test()
# #     interval_test.analyze(df,f"PnL at {interval}")

# ####### Test Optimized Parameters #######
# def test_optimized(symbol, start_date, end_date, time_interval):
#     """
#     Test the strategy using the optimized parameters
#     """
#     df = tools.setup(symbol, start_date, end_date, time_interval)
    
#     ####### Test Optimized Parameters #######
#     basic_optimization = BasicOptimization(df, symbol, start_date, end_date, time_interval)
#     best_parameters = basic_optimization.optimize()
#     optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = basic_optimization.get_optimized_parameters()
#     o = tester(symbol, start_date, end_date, time_interval, optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
#     o.test()
#     graph_title = f"Optimized {symbol} - {year} {time_interval}" 
#     o.analyze(graph_title)
#     print("Best parameters:", best_parameters)

#     return optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight

# # optimized_position_size, optimized_rsi_high, optimized_rsi_low, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight = test_optimized(symbol, start_date, end_date, time_interval)

# ''' Need to test on 2022 and see if using this program earlier can save the portfolio'''


# ####### Testing on a Different Year #######
# # symbol = 'AMD'
# # year = 2021
# # start_date, end_date = date(year,1,1) , date(year,12,31)

# # print("Default Parameters Set")

# # print("Testing Default Strategy")
# # t = tester(symbol,start_date,end_date,time_interval, optimized_rsi_high, optimized_rsi_low, optimized_position_size, optimized_take_profit, optimized_stop_loss, optimized_rsi_weight, optimized_macd_weight, optimized_bb_weight)
# # t.test()
# # graph_title = f"{symbol} - {year} {time_interval}"
# # t.analyze(graph_title)