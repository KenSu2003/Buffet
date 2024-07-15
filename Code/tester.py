import csv, os
import testing_tools as tools
from strategies import Momentum

class tester:

    def __init__(self, 
                 symbol, crypto_or_stock,
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

        self.df = tools.setup(self.symbol, crypto_or_stock, self.start_date, self.end_date, self.time_interval)  # fetch data


    def test(self):
        strategy = Momentum(self.df)
        strategy.evaluate_indicators()
        df = self.simulate_all_trades()    # implement strategy, determine BUY/SELL signal    
        self.df = df
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
        
        file_path = "./data"

        # Calculate PNL
        pnl, roi = tools.calculate_pnl(self.df, self.position_size, self.take_profit, self.stop_loss) 
        print(f"Total PnL: ${pnl:.2f}\t({roi*100:.2f}%)")
        year = f"{self.start_date.year}-{self.end_date.year}"

        # Save the Technical Indicator Datafile
        filename = f"{file_path}/TI_{self.symbol}_{year}_{self.time_interval}.csv"

        # Ensure the directory for the filename exists
        os.makedirs(os.path.dirname(filename), exist_ok=True)

        # Save data to csv file, export to CSV to analyze the data more easily  
        self.df.to_csv(filename)

        # Save year and PnL to CSV file
        file_name = f"{file_path}/pnl_record_{title}.csv"

        # Ensure the directory for the PnL record exists
        os.makedirs(os.path.dirname(file_name), exist_ok=True)

        with open(file_name, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerow([year, pnl])

        
        graph_title = f"{file_path}/{title}"

        # Ensure the directory for the graph_title record exists
        os.makedirs(os.path.dirname(graph_title), exist_ok=True)

        # Plot the trades
        tools.plot(self.df, graph_title)    
