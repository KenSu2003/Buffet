
import talib

def add_technical_indicators(df):
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)
    df['MACD'], df['MACD_signal'], df['MACD_hist'] = talib.MACD(df['Close'])
    df['BB_upper'], df['BB_middle'], df['BB_lower'] = talib.BBANDS(df['Close'])
    df.dropna(inplace=True)
    return df

# Adding technical indicators
# df = add_technical_indicators(df)
