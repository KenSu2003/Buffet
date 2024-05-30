'''  
    If the RSI is above RSI_HIGH that means the stock is overbought
    If the RSI is below RSI_LOW that means the stock is underbought
    If the RSI is between RSI_HIGH aand RSI_LOW remain neutral

    Acceleration —> Direction —> Bullish (+) and Bearish (-)
    
    If the RSI goes below the RSI-EWMA is above RSI-HIGH —> Bearish
    If the RSI goes above the RSI-EWMA & RSI[-1] is below RSI-LOW —> Bullish
'''
def calc_RSI(df, RSI_HIGH, RSI_LOW):
    df['RSI_signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
    for i in range(1,len(df)):
        if df['RSI'].iloc[i] > df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] < df['RSI_ema'].iloc[i-1]:   # BUY
            df['RSI_signal'].iloc[i] = 1
            if df['RSI'].iloc[i] < RSI_LOW: df['RSI_signal'].iloc[i] = 2
        elif df['RSI'].iloc[i] < df['RSI_ema'].iloc[i] and df['RSI'].iloc[i-1] > df['RSI_ema'].iloc[i-1]: # SELL
            df['RSI_signal'].iloc[i] = -1
            if df['RSI'].iloc[i] > RSI_HIGH: df['RSI_signal'].iloc[i] = -2
        else:
            df['RSI_signal'].iloc[i] = 0
    return df


'''  
    If the MACD flips from red to green with high volume that means —> Bullish
    If the MACD flips from green to red with high volume that means —> Bearish
    If the volume is decreasing that means the momentum is going down so prepare to close position.
'''
def calc_MACD(df):
    df['MACD_flip'] = 0
    for i in range(1, len(df)):
        if df['MACD'].iloc[i] > df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] <= df['MACD_signal'].iloc[i-1]:
            df['MACD_flip'].iloc[i] = 1  # Flip from red to green
        elif df['MACD'].iloc[i] < df['MACD_signal'].iloc[i] and df['MACD'].iloc[i-1] >= df['MACD_signal'].iloc[i-1]:
            df['MACD_flip'].iloc[i] = -1  # Flip from green to red
    return df


'''  
    If the Bolligner Bands are divierging that means there is a large price movement. 

    MUCH MORE DIFFICULT TO IMPLEMENT
    1. Find average NORMALIZED level

'''
def calc_BB(df):
    df['BB_width'] = df['BB_upper'] - df['BB_lower']
    df['BB_diverging'] = 0
    for i in range(1, len(df)):
        if df['BB_width'].iloc[i] > df['BB_width'].iloc[i-1]:
            df['BB_diverging'].iloc[i] = 1  # Bands are diverging
        elif df['BB_width'].iloc[i] < df['BB_width'].iloc[i-1]:
            df['BB_diverging'].iloc[i] = -1  # Bands are converging
    return df


def trade(df):
    df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
    for i in range(len(df)):
        df['Signal'].iloc[i] = df['RSI_signal'].iloc[i] + df['RSI_signal'].iloc[i] + df['BB_diverging'].iloc[i]
        # df.loc[i, 'signal'] = df['RSI_signal'].iloc[i] + df['RSI_signal'].iloc[i] + df['BB_diverging'].iloc[i]
    return df