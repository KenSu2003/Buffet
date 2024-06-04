import pandas as pd
import warnings

warnings.simplefilter(action='ignore', category=FutureWarning)

def calc_RSI(df, RSI_HIGH=70, RSI_LOW=30):
    """  
    If the RSI is above RSI_HIGH that means the stock is overbought
    If the RSI is below RSI_LOW that means the stock is underbought
    If the RSI is between RSI_HIGH aand RSI_LOW remain neutral

    Acceleration —> Direction —> Bullish (+) and Bearish (-)
    
    If the RSI goes below the RSI-EWMA is above RSI-HIGH —> Bearish
    If the RSI goes above the RSI-EWMA & RSI[-1] is below RSI-LOW —> Bullish
    """
    
    df['RSI_signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
    for i in range(1,len(df)):
        if df['RSI'].iloc[i] > df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] < df['RSI_ema'].iloc[i-1]:   # BUY
            df.at[df.index[i], 'RSI_signal'] = 1
            if df['RSI'].iloc[i] < RSI_LOW: df.at[df.index[i], 'RSI_signal'] = 2   # df['RSI_signal'].iloc[i] = 2
        elif df['RSI'].iloc[i] < df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] > df['RSI_ema'].iloc[i-1]: # SELL
            df.at[df.index[i], 'RSI_signal'] = -1
            if df['RSI'].iloc[i] > RSI_HIGH: df.at[df.index[i], 'RSI_signal'] = -2   # df['RSI_signal'].iloc[i] = -2
        else:
            df.at[df.index[i], 'RSI_signal'] = 0
    return df

def calc_MACD(df):
    """
    If the MACD flips from red to green with high volume that means —> Bullish
    If the MACD flips from green to red with high volume that means —> Bearish
    If the volume is decreasing that means the momentum is going down so prepare to close position.
    """

    df['MACD_flip'] = 0
    for i in range(1, len(df)):
        if df['MACD'].iloc[i] > df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] <= df['MACD_signal'].iloc[i-1]:
            df.at[df.index[i], 'MACD_flip'] = 1     # Flip from red to green
        elif df['MACD'].iloc[i] < df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] >= df['MACD_signal'].iloc[i-1]:
            df.at[df.index[i], 'MACD_flip'] = -1    # Flip from green to red
    return df

def calc_BB(df):
    """
    Calculates the buy/sell signal from the Bollinger Bands.
    If the Bolligner Bands are diverging that means there is a large price movement ahead. (signal=1)
    If the Bollinger Bands are converging that means there is consolidation ahead. (signal=-1)
    
    :return: The function returns 1 if the BBs are diverging and -1 if they are converging
    """

    df['BB_width'] = df['BB_upper'] - df['BB_lower']
    df['BB_diverging'] = 0
    for i in range(1, len(df)):
        if df['BB_width'].iloc[i] > df['BB_width'].iloc[i-1]:
            df.at[df.index[i], 'BB_diverging'] = 1    # Bands are diverging
        elif df['BB_width'].iloc[i] < df['BB_width'].iloc[i-1]:
            df.at[df.index[i], 'BB_diverging'] = -1   # Bands are converging
    return df

def trade_date(df, trading_date, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
    """
    Evaluates whether to BUY or SELL on a given date using the strategy.

    :param trading_date: the date you want to evaluate
    :param RSI_WEIGHT: the significance of the RSI signal (default=1)
    :param MACD_WEIGHT: the significance of the MACD signal (default=1)
    :param BB_WEIGHT:   the significance of the Bolling Bands' signal (default=1)
    :return: returns the buy/sell trade signal (-2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY)
    """

    buy_sell_signal = 0
    i = df.index.get_loc(trading_date)       # need to include check if it's a trading date
    rsi_signal = df.at[df.index[i], 'RSI_signal']
    macd_signal = df.at[df.index[i], 'MACD_signal']
    bb_signal = df.at[df.index[i], 'BB_diverging']
    buy_sell_signal = rsi_signal*RSI_WEIGHT + macd_signal*MACD_WEIGHT + bb_signal*BB_WEIGHT
    return buy_sell_signal

def simulate_trades(df, RSI_HIGH=70, RSI_LOW=30, RSI_WEIGHT=1, MACD_WEIGHT=1, BB_WEIGHT=1):
    """
    Simulate all the trades in the given time frame based on the given parameter using this strategy.
    """

    df = calc_RSI(df, RSI_HIGH, RSI_LOW)    # RSI
    df = calc_MACD(df)                      # MACD
    df = calc_BB(df)                        # Bollinger Bands

    df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
    for i in range(len(df)):
        # Calculate the new signal value directly
        signal_value = df.at[df.index[i], 'RSI_signal']*RSI_WEIGHT + df.at[df.index[i], 'MACD_signal']*MACD_WEIGHT + df.at[df.index[i], 'BB_diverging']*BB_WEIGHT
        df.at[df.index[i], 'Signal'] = float(signal_value)  # float (not int) makes it more accurate

    return df

