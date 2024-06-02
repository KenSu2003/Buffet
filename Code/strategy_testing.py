import matplotlib.pyplot as plt
import csv
import strategy_tools, strategy1
from datetime import date


class tester:

    def __init__(self, 
                 symbol, 
                 start_date, end_date, time_interval,       
                 RSI_HIGH, RSI_LOW,
                 POSITION_SIZE, TAKE_PROFIT, STOP_LOSS):

        self.symbol = symbol

        # Time (time-period, time-interval)
        self.start_date = start_date
        self.end_date = end_date
        self.time_interval = time_interval

        # Indicators
        self.RSI_HIGH = RSI_HIGH
        self.RSI_LOW = RSI_LOW
        self.POSITION_SIZE = POSITION_SIZE
        self.TAKE_PROFIT = TAKE_PROFIT
        self.STOP_LOSS = STOP_LOSS

        self.RSI_WEIGHT = 1
        self.MACD_WEIGHT = 1
        self.BB_WEIGHT = 1
        
    def test(self):
        df = strategy_tools.setup(self.symbol, self.start_date, self.end_date, self.time_interval)  # fetch data          
        df = strategy1.trade(df, self.RSI_HIGH, self.RSI_LOW, self.RSI_WEIGHT, self.MACD_WEIGHT, self.BB_WEIGHT)    # implement strategy, determine BUY/SELL signal    
        return df

    def analyze(self, df, title):
        # Calculate PNL
        pnl = strategy_tools.calculate_pnl(df, self.TAKE_PROFIT, self.STOP_LOSS, self.POSITION_SIZE) 
        print(f"Total PnL: ${pnl:.2f}")

        df.to_csv('technical_indicators.csv')       # Save data to csv file, export to CSV to analyze the data more easily  
        
        strategy_tools.plot(plt, df, title)    # Plot the trade signals

        # Save year and PnL to CSV file
        with open('pnl_record.csv', mode='a', newline='') as file:
            writer = csv.writer(file)
            year = f"{self.start_date.year}-{self.end_date.year}"
            writer.writerow([year, pnl])


# ——————————————————- Run Tests ————————————————————

# Parameters
symbol = 'AMD'
start_date, end_date, time_interval = date(2022,1,1) , date(2022,12,31)  , '1d'
RSI_HIGH, RSI_LOW = 77, 32
POSITION_SIZE, TAKE_PROFIT, STOP_LOSS = 1990, 5, 4      # Opitimized 2020 parameters

# Test Different Years
years = [2019, 2020, 2021, 2022, 2023]
for year in range (2019,2024):
    start_date = date(year,1,1)
    end_date = date(year,12,31)
    years_test = tester(symbol,start_date,end_date,time_interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
    df = years_test.test()
    graph_title = f"PnL in {year}"
    years_test.analyze(df, graph_title)

# Test Different Intervals
# intervals = ['1d','5d','1wk','1mo','3mo']
# for interval in intervals:
#     interval_test = tester(symbol,start_date,end_date,interval,RSI_HIGH,RSI_LOW,POSITION_SIZE,TAKE_PROFIT,STOP_LOSS)
#     df = interval_test.test()
#     interval_test.analyze(df,f"PnL at {interval}")