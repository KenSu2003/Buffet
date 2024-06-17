from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime
import pandas as pd

def setup(symbol_or_sumbols,start_time,end_time):
    # Replace with your Alpaca API keys
    APCA_API_KEY_ID = "PKDSUFSDD8XOZZC309LK"
    APCA_API_SECRET_KEY = "araI1T7gB3rsXErEanFI9QwIdyQeVE8XUgGOMtey"

    data = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

    request_params = StockBarsRequest(
                            symbol_or_symbols=symbol_or_sumbols,
                            timeframe=TimeFrame.Day,
                            start=start_time,
                            end=end_time
                    )
    barset = data.get_stock_bars(request_params)

    # df = pd.DataFrame(barset)
    # df.to_csv('output.csv')

    # convert to dataframe
    df = barset.df

    # access bars as list - important to note that you must access by symbol key
    # even for a single symbol request - models are agnostic to number of symbols
    # bars[symbol_or_sumbols]

    return df

symbol = "AMD"
start_time = '2020-01-01'
end_time = '2021-01-01'
df = setup(symbol,start_time,end_time)
# print(df)
filename = f"Alpaca Testing.csv"
df.to_csv(filename)       # Save data to csv file, export to CSV to analyze the data more easily  