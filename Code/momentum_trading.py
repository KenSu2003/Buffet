# A trading strategy outlines the investor's financial goals, 
# including risk tolerance level, 
# long-term and short-term financial needs, 
# tax implications, and time horizon.

import warnings
import strategy_tools
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import date
from pandas import Timestamp

warnings.simplefilter(action='ignore', category=FutureWarning)

class Strategy:

    def __init__(self, df, RSI_HIGH=70, RSI_LOW=30, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
        self.df = df
        self.RSI_HIGH = RSI_HIGH
        self.RSI_LOW = RSI_LOW
        self.RSI_WEIGHT = RSI_WEIGHT
        self.MACD_WEIGHT = MACD_WEIGHT
        self.BB_WEIGHT = BB_WEIGHT

    def calc_RSI(self):
        """  
        If the RSI is above RSI_HIGH that means the stock is overbought
        If the RSI is below RSI_LOW that means the stock is underbought
        If the RSI is between RSI_HIGH aand RSI_LOW remain neutral

        Acceleration —> Direction —> Bullish (+) and Bearish (-)
        
        If the RSI goes below the RSI-EWMA is above RSI-HIGH —> Bearish
        If the RSI goes above the RSI-EWMA & RSI[-1] is below RSI-LOW —> Bullish
        """
        
        self.df['RSI_signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
        for i in range(1,len(self.df)):
            if self.df['RSI'].iloc[i] > self.df['RSI_ema'].iloc[i] and self.df['RSI'].iloc[i-1] < self.df['RSI_ema'].iloc[i-1]:   # BUY
                self.df.at[self.df.index[i], 'RSI_signal'] = 1
                if self.df['RSI'].iloc[i] < self.RSI_LOW: self.df.at[self.df.index[i], 'RSI_signal'] = 2   # self.df['RSI_signal'].iloc[i] = 2
            elif self.df['RSI'].iloc[i] < self.df['RSI_ema'].iloc[i] and self.df['RSI'].iloc[i-1] > self.df['RSI_ema'].iloc[i-1]: # SELL
                self.df.at[self.df.index[i], 'RSI_signal'] = -1
                if self.df['RSI'].iloc[i] > self.RSI_HIGH: self.df.at[self.df.index[i], 'RSI_signal'] = -2   # self.df['RSI_signal'].iloc[i] = -2
            else:
                self.df.at[self.df.index[i], 'RSI_signal'] = 0
        return self.df

    def calc_MACD(self):
        """
        If the MACD flips from red to green with high volume that means —> Bullish
        If the MACD flips from green to red with high volume that means —> Bearish
        If the volume is decreasing that means the momentum is going down so prepare to close position.
        """

        self.df['MACD_flip'] = 0
        for i in range(1, len(self.df)):
            if self.df['MACD'].iloc[i] > self.df['MACD_signal'].iloc[i] and self.df['MACD'].iloc[i-1] <= self.df['MACD_signal'].iloc[i-1]:
                self.df.at[self.df.index[i], 'MACD_flip'] = 1     # Flip from red to green
            elif self.df['MACD'].iloc[i] < self.df['MACD_signal'].iloc[i] and self.df['MACD'].iloc[i-1] >= self.df['MACD_signal'].iloc[i-1]:
                self.df.at[self.df.index[i], 'MACD_flip'] = -1    # Flip from green to red
        return self.df

    def calc_BB(self):
        """
        Calculates the buy/sell signal from the Bollinger Bands.
        If the Bolligner Bands are diverging that means there is a large price movement ahead. (signal=1)
        If the Bollinger Bands are converging that means there is consolidation ahead. (signal=-1)
        
        :return: The function returns 1 if the BBs are diverging and -1 if they are converging
        """

        self.df['BB_width'] = self.df['BB_upper'] - self.df['BB_lower']
        self.df['BB_diverging'] = 0
        for i in range(1, len(self.df)):
            if self.df['BB_width'].iloc[i] > self.df['BB_width'].iloc[i-1]:
                self.df.at[self.df.index[i], 'BB_diverging'] = 1    # Bands are diverging
            elif self.df['BB_width'].iloc[i] < self.df['BB_width'].iloc[i-1]:
                self.df.at[self.df.index[i], 'BB_diverging'] = -1   # Bands are converging
        return self.df

    def evaluate_indicators(self):
        self.df = self.calc_RSI()    # RSI
        self.df = self.calc_MACD()                      # MACD
        self.df = self.calc_BB()                        # Bollinger Bands
        return self.df

    def evaluate(self, rsi_signal, macd_signal, bb_signal):
        return rsi_signal * self.RSI_WEIGHT + macd_signal * self.MACD_WEIGHT + bb_signal * self.BB_WEIGHT
        
    def evaluate_date(self, trading_date):
        """
        Evaluates whether to BUY or SELL on a given date using the strategy.

        :param trading_date: the date you want to evaluate
        :param RSI_WEIGHT: the significance of the RSI signal (default=1)
        :param MACD_WEIGHT: the significance of the MACD signal (default=1)
        :param BB_WEIGHT:   the significance of the Bolling Bands' signal (default=1)
        :return: returns the buy/sell trade signal (-2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY)
        """

        trading_signal = 0
        trading_date = Timestamp(trading_date).date()       # Convert trading_date to a date object
        date_index = self.df.index.date         # Convert DataFrame index to date only for comparison

        if trading_date not in date_index:
            print("Not a Trading Day or Date not found in DataFrame")
        else:
            i = list(date_index).index(trading_date)  # Find the first occurrence in the date index
            rsi_signal = self.df.at[self.df.index[i], 'RSI_signal']
            macd_signal = self.df.at[self.df.index[i], 'MACD_signal']
            bb_signal = self.df.at[self.df.index[i], 'BB_diverging']
            trading_signal = self.evaluate(rsi_signal, macd_signal, bb_signal)

        return trading_signal


#### Test ####
# stock = 'AMD'
# start_time = date(2022,1,1)
# end_time = date(2022,12,31)
# interval = TimeFrame(1,TimeFrameUnit.Day)

# df = strategy_tools.setup(stock,start_time,end_time,interval)

# strategy1 = Strategy(df)
# strategy1.evaluate_indicators()
# # strategy1.simulate_trades()
# # print(strategy1.df)

# # print(strategy1.df.index)
# trading_date = date(2022,3,28)
# print(strategy1.evaluate_date(trading_date))



# file_path = "./Data"
# year = start_time.year

# filename = f"{file_path}/TI_{stock}_{year}_{interval}.csv"
# strategy1.df.to_csv(filename)       # Save data to csv file, export to CSV to analyze the data more easily  
