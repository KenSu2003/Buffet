import warnings
import testing_tools as tools
from alpaca.data.timeframe import TimeFrame, TimeFrameUnit
from datetime import date
from pandas import Timestamp

warnings.simplefilter(action='ignore', category=FutureWarning)

class Momentum:

    def __init__(self, df, RSI_HIGH=70, RSI_LOW=30, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
        self.df = df
        self.RSI_HIGH = RSI_HIGH
        self.RSI_LOW = RSI_LOW
        self.RSI_WEIGHT = RSI_WEIGHT
        self.MACD_WEIGHT = MACD_WEIGHT
        self.BB_WEIGHT = BB_WEIGHT

    def calc_RSI_signal(self, rsi, rsi_ema, rsi_prev, rsi_ema_prev):
        """The function calculates for the RSI signal with the given RSI values.

        Args:
            rsi (float): The rsi value on the given time-interval.
            rsi_ema (float): The rsi-ema (exponential moving average) on the give time-interval.
            rsi_prev (_type_): _description_
            rsi_ema_prev (_type_): _description_

        Returns:
            int: The calcualed RSI signal.
        """        

        if rsi > rsi_ema and rsi_prev < rsi_ema_prev:
            return 1 if rsi < self.RSI_LOW else 2
        elif rsi < rsi_ema and rsi_prev > rsi_ema_prev:
            return -1 if rsi > self.RSI_HIGH else -2
        return 0

    def calc_RSI(self):
        """  
        If the RSI is above RSI_HIGH that means the stock is overbought
        If the RSI is below RSI_LOW that means the stock is underbought
        If the RSI is between RSI_HIGH aand RSI_LOW remain neutral

        Acceleration —> Direction —> Bullish (+) and Bearish (-)
        
        If the RSI goes below the RSI-EWMA is above RSI-HIGH —> Bearish
        If the RSI goes above the RSI-EWMA & RSI[-1] is below RSI-LOW —> Bullish

        Returns:    
            df (datafile): returns the datafile with calculated RSI
        """
        
        self.df['RSI_signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
        for i in range(1,len(self.df)):
            rsi = self.df['RSI'].iloc[i]
            rsi_ema = self.df['RSI_ema'].iloc[i]
            rsi_prev = self.df['RSI'].iloc[i-1]
            rsi_ema_prev = self.df['RSI_ema'].iloc[i-1]
            self.df.at[self.df.index[i], 'RSI_signal'] = self.calc_RSI_signal(rsi, rsi_ema, rsi_prev, rsi_ema_prev)
        return self.df

    def calc_MACD_signal(self, macd, macd_signal, macd_prev, macd_signal_prev):
        if macd > macd_signal and macd_prev <= macd_signal_prev:
            return 1    # Flip from red to green
        elif macd < macd_signal and macd_prev >= macd_signal_prev:
            return -1   # Flip from green to red
        return 0

    def calc_MACD(self):
        """
        If the MACD flips from red to green with high volume that means —> Bullish
        If the MACD flips from green to red with high volume that means —> Bearish
        If the volume is decreasing that means the momentum is going down so prepare to close position.
        """
        self.df['MACD_flip'] = 0
        for i in range(1, len(self.df)):
            macd = self.df['MACD'].iloc[i]
            macd_signal = self.df['MACD_signal'].iloc[i]
            macd_prev = self.df['MACD'].iloc[i-1]
            macd_signal_prev = self.df['MACD_signal'].iloc[i-1]
            self.df.at[self.df.index[i], 'MACD_flip'] = self.calc_MACD_signal(macd, macd_signal, macd_prev, macd_signal_prev)
        return self.df

    def calc_BB_signal(self, bb_upper, bb_lower, bb_upper_prev, bb_lower_prev):
        bb_width = bb_upper-bb_lower
        bb_width_prev = bb_upper_prev-bb_lower_prev
        if bb_width > bb_width_prev:
            return 1    # Bands are diverging
        elif bb_width < bb_width_prev:
            return -1   # Bands are converging
        return 0

    def calc_BB(self):
        """
        Calculates the buy/sell signal from the Bollinger Bands.
        If the Bolligner Bands are diverging that means there is a large price movement ahead. (signal=1)
        If the Bollinger Bands are converging that means there is consolidation ahead. (signal=-1)
        
        :return: The function returns 1 if the BBs are diverging and -1 if they are converging
        """
        
        for i in range(1, len(self.df)):
            bb_upper = self.df['BB_upper'].iloc[i]
            bb_lower = self.df['BB_lower'].iloc[i]
            bb_upper_prev = self.df['BB_upper'].iloc[i-1]
            bb_lower_prev = self.df['BB_lower'].iloc[i-1]
            self.df.at[self.df.index[i], 'BB_diverging'] = self.calc_BB_signal(bb_upper, bb_lower, bb_upper_prev, bb_lower_prev)
        return self.df

    def evaluate_indicators(self):
        self.df = self.calc_RSI()    # RSI
        self.df = self.calc_MACD()                      # MACD
        self.df = self.calc_BB()                        # Bollinger Bands
        return self.df
    
    def evaluate_latest(self):

        rsi = self.df['RSI'].iloc[-1]
        rsi_ema = self.df['RSI_ema'].iloc[-1]
        rsi_prev = self.df['RSI'].iloc[-2]
        rsi_ema_prev = self.df['RSI_ema'].iloc[-2]
        
        macd = self.df['MACD'].iloc[-1]
        macd_signal = self.df['MACD_signal'].iloc[-1]
        macd_prev = self.df['MACD'].iloc[-2]
        macd_signal_prev = self.df['MACD_signal'].iloc[-2]
        
        bb_upper = self.df['BB_upper'].iloc[-1]
        bb_lower = self.df['BB_lower'].iloc[-1]
        bb_upper_prev = self.df['BB_upper'].iloc[-2]
        bb_lower_prev = self.df['BB_lower'].iloc[-2]

        return self.evaluate(self.calc_RSI_signal(rsi, rsi_ema, rsi_prev, rsi_ema_prev), self.calc_MACD_signal(macd, macd_signal, macd_prev, macd_signal_prev), self.calc_BB_signal(bb_upper, bb_lower, bb_upper_prev, bb_lower_prev))


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

# https://www.investopedia.com/terms/l/longstraddle.asp#:~:text=Error%20Code%3A%20100013)-,What%20Is%20Long%20Straddle%3F,asset%20following%20a%20market%20event.
class Straddle:
    '''
    If expecting a large price movement but uncertain which direction Straddle
    '''

    def __init__(self):
        self.signal = 0     # 1 = Long Call and Long Put , -1 = Short Call and Short Put

    def calc_macd(self):
        pass
    
    def evaluate(self):
        if self.signal==1:
            self.long_straddle()

    
    def long_straddle():
        pass

# https://learn.bybit.com/indicators/best-swing-trading-indicators/
class Swing:
    '''
    RSI (Prediction) 70/30, center line
    MA (Confirmation) 
    '''

    def __init__(self) -> None:
        pass

# def sigmoid(x):
#     return 1 / (1 + math.exp(-x))

# def transform_signal(signal):
#     # Apply sigmoid transformation and scale to range [-1, 1]
#     return 2 * sigmoid(signal) - 1

def calculate_order_size(starting_balance, current_account_balance, signal, max_position_size_percentage, current_position_size_dollars, capital_per_symbol_start):
    # Check if the signal is within the no-trade range
    if -1 <= signal <= 1:
        return 0  # No trade

    # Scale factor based on the current balance relative to the starting balance
    balance_scale = current_account_balance / starting_balance

    # Calculate the preliminary order size in dollars based on the capital allocation per symbol
    preliminary_order_size_dollars = balance_scale * abs(signal) * capital_per_symbol_start

    # Calculate the maximum allowable position size in dollars based on the current account balance
    max_position_size_dollars = max_position_size_percentage * current_account_balance

    if max_position_size_dollars ==0: return 0

    # Adjust the order size based on the signal direction
    if signal > 0:
        # Buy signal
        if max_position_size_dollars - current_position_size_dollars <= 0: order_size_dollars = 0
        else: order_size_dollars = min(preliminary_order_size_dollars, max_position_size_dollars - current_position_size_dollars, current_account_balance)
    else:
        # Sell signal
        order_size_dollars = min(preliminary_order_size_dollars, current_position_size_dollars)
    
    return order_size_dollars