import csv
import yfinance as yf
import talib
import pandas as pd

# trading on 1d not 1h so not as practical

def setup(symbol, start_date, end_date, time_interval):
    """
    Download the stock price history within the given time frame.

    :param symbol: the symbol of the stock to test the strategy with
    :param start_date: the start date of the data to be downloaded
    :param end_date: the end date of the data to be downloaded
    :time_interval: intervals of the the closing price ['1m','2m','5m','15m','30m','60m','90m','1h','1d','5d','1wk','1mo','3mo']
    :return: the data file
    """

    df = yf.download(symbol, start=start_date, end=end_date, interval=time_interval)    # fetch stock data

    # Retrieve Indicators
    df['BB_upper'], df['BB_mid'], df['BB_lower'] = talib.BBANDS(df['close'], timeperiod=20)     # Bollingner Bands
    df['MACD'], df['MACD_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)    # MACD
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)   # RSI
    df['RSI_ema'] = talib.EMA(df['RSI'], timeperiod=14)  # Calculate RSI-EMA
    df['Volume'] = df['Volume'] # Volume

    # df.dropna(inplace=True) # Remove NULL values
    print("Setup Successful")
    return df


# should consider implementing margin
def calculate_pnl(data, profit_target_pct, stop_loss_pct, trade_size):
    """
    Calcualte the profit and loss (PnL) as well as the Return on Investment (ROI).
    Saves the trades in the file trades.csv.

    :param data: the data file (default=df)
    :param profit_target_pct: the take-profit level in percentage (%) not in decimal (.)
    :param stop_loss_pct: the stop-loss level in percentage (%) not in decimal (.)
    :param trade_size: the size of the positon in $
    :return: returns the PnL and the roi
    """

    trades = []
    position = 0  # 1 for long, -1 for short, 0 for no position
    entry_price = 0
    profits = []
    rois = []

    for i in range(len(data)):
        if position == 0:
            if data['Signal'].iloc[i] > 0:
                position = 1
                entry_price = data['close'].iloc[i]
            elif data['Signal'].iloc[i] < 0:
                position = -1
                entry_price = data['close'].iloc[i]
        elif position == 1:
            if data['close'].iloc[i] >= entry_price * (1 + profit_target_pct / 100) or \
               data['close'].iloc[i] <= entry_price * (1 - stop_loss_pct / 100):
                
                # roi = (data['close'].iloc[i] - entry_price) * trade_size / entry_price     # in %
                roi = (data['close'].iloc[i] - entry_price) / entry_price                   # in %
                pnl = (data['close'].iloc[i] - entry_price) * (trade_size/entry_price)      # in $
                profits.append(pnl)
                rois.append(roi)
                data.at[data.index[i], 'PnL'] = pnl
                data.at[data.index[i], 'ROI'] = roi

                trades.append((entry_price, data['close'].iloc[i], position, pnl, roi))
                position = 0
        elif position == -1:
            if data['close'].iloc[i] <= entry_price * (1 - profit_target_pct / 100) or \
               data['close'].iloc[i] >= entry_price * (1 + stop_loss_pct / 100):
                
                # roi = (entry_price - data['close'].iloc[i]) * trade_size / entry_price     # in %
                roi = (entry_price - data['close'].iloc[i]) / entry_price                   # in %
                pnl = (entry_price - data['close'].iloc[i]) * (trade_size/entry_price)      # in $
                profits.append(pnl)
                rois.append(roi)
                data.at[data.index[i], 'PnL'] = pnl
                data.at[data.index[i], 'ROI'] = roi

                trades.append((entry_price, data['close'].iloc[i], position, pnl, roi))
                position = 0

    with open('trades.csv', 'w', newline='') as f:
        fields = ['entry', 'exit', 'pos', 'roi']
        # writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer = csv.writer(f)
        # writer.writeheader()
        writer.writerows(list(trades))

    return sum(profits), sum(rois)


def plot(plt, df, graph_title):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['close'], label='close Price', color='blue')
    # plt.plot(pd.to_datetime(df.index.get_level_values('timestamp')), df['close'], label='close Price', color='blue')
    plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['close'], marker='^', color='g', label='Buy Signal')
    plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['close'], marker='v', color='r', label='Sell Signal')
    plt.title('Buy and Sell Signals on AMD Historical Data')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig("%s.png"%graph_title)
    print("Graph Plotted")
