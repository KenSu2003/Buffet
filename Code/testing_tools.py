import csv, os
import talib, math
import matplotlib.pyplot as plt
from alpaca_api import crypto_client, stock_client, CryptoBarsRequest, StockBarsRequest, get_open_position, get_balance


def setup(symbol_or_symbols,crypto_or_stock,start_time,end_time,interval):
    """
    Download the asset price history within the given timeframe.

    Args:
        symbol_or_symbols (str or list): The symbol(s) of the asset(s) to fetch data for.
        crypto_or_stock (str): Indicates whether the symbol(s) is/are cryptocurrency or stock.
        start_time (str): The start time of the data to be downloaded (format: 'YYYY-MM-DD').
        end_time (str): The end time of the data to be downloaded (format: 'YYYY-MM-DD').
        interval (TimeFrame): The interval for the data using Alpaca TimeFrame.

    Returns:
        DataFrame: A DataFrame containing historical price data and calculated technical indicators.
    """
    if crypto_or_stock == 'crypto':
        request_params = CryptoBarsRequest(
                                symbol_or_symbols=symbol_or_symbols,
                                timeframe=interval,
                                start=start_time,
                                end=end_time
                        )
        barset = crypto_client.get_crypto_bars(request_params)
    elif crypto_or_stock == 'stock':
        request_params = StockBarsRequest(
                                symbol_or_symbols=symbol_or_symbols,
                                timeframe=interval,
                                start=start_time,
                                end=end_time
                        )
        barset = stock_client.get_stock_bars(request_params)
    else:
        print("crypto or stock not sepcified")
        return

    df = barset.df      # convert to dataframe
    df = df.reset_index(level='symbol', drop=True)

    # Retrieve Indicators
    df['BB_upper'], df['BB_mid'], df['BB_lower'] = talib.BBANDS(df['close'], timeperiod=20)     # Bollingner Bands
    df['MACD'], df['MACD_signal'], _ = talib.MACD(df['close'], fastperiod=12, slowperiod=26, signalperiod=9)    # MACD
    df['RSI'] = talib.RSI(df['close'], timeperiod=14)   # RSI
    df['RSI_ema'] = talib.EMA(df['RSI'], timeperiod=14)  # Calculate RSI-EMA
    df['Volume'] = df['volume']     # Volume
    # df.dropna(inplace=True) # Remove NULL values  
  
    return df


# should consider implementing margin
def calculate_pnl(data, trade_size, profit_target_pct, stop_loss_pct):
    """
    Calculate the profit and loss (PnL) as well as the Return on Investment (ROI).
    Saves the trades in the file trades.csv.

    Args:
        data (DataFrame): The DataFrame containing trade data and signals.
        trade_size (float): The size of the position in dollars.
        profit_target_pct (float): The take-profit level in percentage.
        stop_loss_pct (float): The stop-loss level in percentage.

    Returns:
        tuple: A tuple containing the total PnL (in dollars) and the average ROI (in percentage).
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

    file_path = "./data"
    filename = f"{file_path}/trades.csv"

    # Ensure the directory for the trades record exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, 'w', newline='') as f:
        fields = ['entry', 'exit', 'pos', 'roi']
        # writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer = csv.writer(f)
        # writer.writeheader()
        writer.writerows(list(trades))

    return sum(profits), sum(rois)


def plot(df, graph_title):
    """
    Plots the historical price data along with buy and sell signals.

    Args:
        df (DataFrame): The DataFrame containing price data and signals.
        graph_title (str): The title and file path for saving the plot.
    """
    x_scale = 1
    y_scale = 1
    signal_scale=1
    plt.figure(figsize=(14*x_scale, 7*y_scale), dpi=300)
    plt.plot(df.index, df['close'], label='close Price', color='blue')
    plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['close'], marker='^', color='g', label='Buy Signal', s=24*signal_scale)
    plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['close'], marker='v', color='r', label='Sell Signal', s=24*signal_scale)
    plt.title("Buy and Sell Signals on \{symbol\} Historical Data")
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig("%s.png"%graph_title)
    print("Graph Plotted")


def simulate_trades(df, rsi_weight=1, macd_weight=1, bb_weight=1):
    """
    Simulates all the trades based on the given weights for technical indicators.

    Args:
        df (DataFrame): The DataFrame containing price data and indicators.
        rsi_weight (float, optional): The weight for the RSI indicator. Default is 1.
        macd_weight (float, optional): The weight for the MACD indicator. Default is 1.
        bb_weight (float, optional): The weight for the Bollinger Bands indicator. Default is 1.

    Returns:
        DataFrame: The DataFrame with added signals based on the simulation.
    """
    df['Signal'] = 0      # -2: STRONG SELL, -1: SELL, 0: NEUTRAL, 1: BUY, 2: STRONG BUY
    for i in range(len(df)):
        # Calculate the new signal value directly
        signal_value = df.at[df.index[i], 'RSI_signal']*rsi_weight + df.at[df.index[i], 'MACD_signal']*macd_weight + df.at[df.index[i], 'BB_diverging']*bb_weight
        df.at[df.index[i], 'Signal'] = float(signal_value)  # float (not int) makes it more accurate
    return df


