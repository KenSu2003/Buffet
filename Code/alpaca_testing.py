from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
import talib


def setup(symbol_or_sumbols,start_time,end_time,interval):
    """
    Download the stock price history within the given time frame.

    :param symbol: the symbol of the stock to test the strategy with
    :param start_date: the start date of the data to be downloaded
    :param end_date: the end date of the data to be downloaded
    :time_interval: intervals of the the closing price ['1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo']
    :return: the data file
    """

    # Replace with your Alpaca API keys
    APCA_API_KEY_ID = "PKDSUFSDD8XOZZC309LK"
    APCA_API_SECRET_KEY = "araI1T7gB3rsXErEanFI9QwIdyQeVE8XUgGOMtey"

    data = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

    request_params = StockBarsRequest(
                            symbol_or_symbols=symbol_or_sumbols,
                            timeframe=interval,
                            start=start_time,
                            end=end_time
                    )
    barset = data.get_stock_bars(request_params)
    df = barset.df      # convert to dataframe
    df = df.reset_index(level='symbol', drop=True)
    # print(df.index.get_level_values('timestamp'))
    # Retrieve Indicators
    df['BB_upper'], df['BB_mid'], df['BB_lower'] = talib.BBANDS(df['close'], timeperiod=20)     # Bollingner Bands
    df['MACD'], df['MACD_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)    # MACD
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)   # RSI
    df['RSI_ema'] = talib.EMA(df['RSI'], timeperiod=14)  # Calculate RSI-EMA
    df['Volume'] = df['volume'] # Volume

    # df.dropna(inplace=True) # Remove NULL values
    print("Setup Successful")
    
    return df

# symbol = "AMD"
# start_time = '2020-01-01'
# end_time = '2021-01-01'
# df = setup(symbol,start_time,end_time)
# # print(df)
# filename = f"Alpaca Testing.csv"
# df.to_csv(filename)       # Save data to csv file, export to CSV to analyze the data more easily  