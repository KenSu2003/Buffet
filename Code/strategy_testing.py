import matplotlib.pyplot as plt
import csv
import strategy_tools as tools
import momentum_trading as strategy
from datetime import date
from optimize_strategy import BasicOptimization
from alpaca.data.timeframe import TimeFrame


class tester:

    def __init__(self, 
                 symbol, 
                 start_date, end_date, time_interval,       
                 RSI_HIGH, RSI_LOW,
                 POSITION_SIZE, TAKE_PROFIT, STOP_LOSS,
                 RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):

        self.symbol = symbol

        # Time (time-period, time-interval)
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

        # Indicators
        self.RSI_HIGH = RSI_HIGH
        self.RSI_LOW = RSI_LOW
        self.POSITION_SIZE = POSITION_SIZE          # number of stocks not $
        self.TAKE_PROFIT = TAKE_PROFIT              # in % not .
        self.STOP_LOSS = STOP_LOSS                  # in % not .

        self.RSI_WEIGHT = RSI_WEIGHT
        self.MACD_WEIGHT = MACD_WEIGHT
        self.BB_WEIGHT = BB_WEIGHT

        self.df = {}
    
    
    def test(self):
        print("Setting up Alpaca Datafile")
        df = tools.setup(self.symbol, self.start_date, self.end_date, self.time_interval)  # fetch data
        print("Testing Strategy")
        df = strategy.simulate_trades(df, self.RSI_HIGH, self.RSI_LOW, self.RSI_WEIGHT, self.MACD_WEIGHT, self.BB_WEIGHT)    # implement strategy, determine BUY/SELL signal    
        print("Strategy Tested")
        self.df = df
        return df

    def analyze(self, title):
        file_path = "./Data"

        print("Analyzing Data")
        # Calculate PNL
        pnl, roi = tools.calculate_pnl(self.df, self.TAKE_PROFIT, self.STOP_LOSS, self.POSITION_SIZE) 
        print(f"Total PnL: ${pnl:.2f}\t({roi*100:.2f}%)")
        year = f"{self.start_date.year}-{self.end_date.year}"

        print("Saving Datafile")
        filename = f"{file_path}/TI_{self.symbol}_{year}_{self.time_interval}.csv"
        self.df.to_csv(filename)       # Save data to csv file, export to CSV to analyze the data more easily  
        print("Datafile Saved")


        # Save year and PnL to CSV file
        file_name = f"{file_path}/pnl_record_{title}.csv"
        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([year, pnl])
        print("Data Analyzed")

        # Plot the trades
        title = f"{file_path}/{title}"
        tools.plot(plt, self.df, title)    
        
 
# ——————————————————- Run Tests ————————————————————

# Default Parameters
symbol = 'AMD'
year = 2022
start_date, end_date, time_interval = date(year,1,1) , date(year,12,31)  , TimeFrame.Day
RSI_HIGH, RSI_LOW = 70, 30
POSITION_SIZE, TAKE_PROFIT, STOP_LOSS = 1000, 5, 2 
print("Default Parameters Set")

####### Basic Testing #######
# print("Testing Default Strategy")
# t = tester(symbol,start_date,end_date,time_interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
# t.test()
# graph_title = f"{symbol} - {year} {time_interval}"
# t.analyze(graph_title)
# print("BUY/SELL Signal:",strategy.trade_date(df, '2022-03-24'))


####### Alpaca Testing #######
print("Testing Default Strategy")
t = tester(symbol,start_date,end_date,time_interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
t.test()
graph_title = f"{symbol} - {year} {time_interval}"
t.analyze(graph_title)


####### Test Different Years #######
# years = [2019, 2020, 2021, 2022, 2023]
# for year in range (2019,2024):
#     start_date = date(year,1,1)
#     end_date = date(year,12,31)
#     years_test = tester(symbol,start_date,end_date,time_interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
#     df = years_test.test()
#     graph_title = f"PnL in {year}"
#     years_test.analyze(df, graph_title)

####### Test Different Intervals #######
# intervals = ['1d','5d','1wk','1mo','3mo']
# for interval in intervals:
#     interval_test = tester(symbol,start_date,end_date,interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
#     df = interval_test.test()
#     interval_test.analyze(df,f"PnL at {interval}")

####### Test Optimized Parameters #######
def test_optimized(symbol, start_date, end_date, time_interval):
    """
    Test the strategy using the optimized parameters
    """
    df = tools.setup(symbol, start_date, end_date, time_interval)
    # df = tools.setup(symbol, start_date, end_date, time_interval)
    ####### Test Optimized Parameters #######
    optimizer = BasicOptimization(df, symbol, start_date, end_date, time_interval).optimize()
    optimized_POSITION_SIZE = optimizer.max['params'].get('POSITION_SIZE')
    optimized_RSI_HIGH = optimizer.max['params'].get('RSI_HIGH')
    optimized_RSI_LOW = optimizer.max['params'].get('RSI_LOW')
    optimized_STOP_LOSS = optimizer.max['params'].get('STOP_LOSS')
    optimized_TAKE_PROFIT = optimizer.max['params'].get('TAKE_PROFIT')

    optimized_RSI_WEIGHT = optimizer.max['params'].get('RSI_WEIGHT')
    optimized_MACD_WEIGHT = optimizer.max['params'].get('MACD_WEIGHT')
    optimized_BB_WEIGHT = optimizer.max['params'].get('BB_WEIGHT')

    o = tester(symbol, start_date, end_date, time_interval, 
            optimized_RSI_HIGH, optimized_RSI_LOW, 
            optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS)
    # df = o.test()
    df = o.test()
    graph_title = f"Optimized {symbol} - {year} {time_interval}"
    o.analyze(graph_title)
    print("Best parameters:", optimizer.max['params'])
    # print("BUY/SELL Signal:",strategy.trade_date(df, '2022-03-24'))

    return optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT

# optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT = test_optimized(symbol, start_date, end_date, time_interval)

####### Testing on a Different Year #######
# symbol = 'AMD'
# year = 2021
# start_date, end_date = date(year,1,1) , date(year,12,31)

# print("Default Parameters Set")

# print("Testing Default Strategy")
# t = tester(symbol,start_date,end_date,time_interval, optimized_RSI_HIGH, optimized_RSI_LOW, optimized_POSITION_SIZE, optimized_TAKE_PROFIT, optimized_STOP_LOSS, optimized_RSI_WEIGHT, optimized_MACD_WEIGHT, optimized_BB_WEIGHT)
# t.test()
# graph_title = f"{symbol} - {year} {time_interval}"
# t.analyze(graph_title)