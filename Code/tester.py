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
        """
        Initializes the tester with the specified parameters and fetches the market data.

        Args:
            symbol (str): The trading symbol (e.g., 'BTC/USD').
            crypto_or_stock (str): Indicates whether the symbol is for a cryptocurrency or a stock.
            start_date (datetime): The start date for testing.
            end_date (datetime): The end date for testing.
            time_interval (TimeFrame): The time interval for fetching data (e.g., hourly).
            rsi_high (float): The high RSI threshold.
            rsi_low (float): The low RSI threshold.
            position_size (int): The size of the trading position.
            take_profit (float): The take profit threshold (in percentage).
            stop_loss (float): The stop loss threshold (in percentage).
            rsi_weight (float, optional): The weight for the RSI indicator. Default is 1.
            macd_weight (float, optional): The weight for the MACD indicator. Default is 1.
            bb_weight (float, optional): The weight for the Bollinger Bands indicator. Default is 1.
        """
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
        """
        Evaluates the strategy using the Momentum class and simulates trades.

        Returns:
            DataFrame: The DataFrame containing the simulated trades with buy/sell signals.
        """
        strategy = Momentum(self.df)
        strategy.evaluate_indicators()
        df = self.simulate_all_trades()    # implement strategy, determine BUY/SELL signal    
        self.df = df
        return df
    
    def calculate_pnl(self):
        """
        Calculates the profit and loss (PnL) from the simulated trades.

        Returns:
            tuple: The total PnL and the return on investment (ROI).
        """
        return tools.calculate_pnl(self.df, self.position_size, self.take_profit, self.stop_loss)
    
    def simulate_all_trades(self):
        """
        Simulates all the trades in the given time frame based on the given parameters using the strategy.

        Returns:
            DataFrame: The DataFrame containing the simulated trades with buy/sell signals.
        """
        self.df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
        for i in range(len(self.df)):
            # Calculate the new signal value directly
            signal_value = self.df.at[self.df.index[i], 'RSI_signal']*self.rsi_weight + self.df.at[self.df.index[i], 'MACD_signal']*self.macd_weight + self.df.at[self.df.index[i], 'BB_diverging']*self.bb_weight
            self.df.at[self.df.index[i], 'Signal'] = float(signal_value)  # float (not int) makes it more accurate
        return self.df

    def analyze(self, title):
        """
        Analyzes the strategy performance, calculates PnL, and saves the results to CSV files.

        Args:
            title (str): The title for the analysis and file naming.
        """
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
