import csv
import yfinance as yf
import talib

def setup(symbol, start_date, end_date, time_interval):

    df = yf.download(symbol, start=start_date, end=end_date, interval=time_interval)    # fetch stock data

    # Retrieve Indicators
    df['BB_upper'], df['BB_mid'], df['BB_lower'] = talib.BBANDS(df['Close'], timeperiod=20)     # Bollingner Bands
    df['MACD'], df['MACD_signal'], _ = talib.MACD(df['Close'], fastperiod=12, slowperiod=26, signalperiod=9)    # MACD
    df['RSI'] = talib.RSI(df['Close'], timeperiod=14)   # RSI
    df['RSI_ema'] = talib.EMA(df['RSI'], timeperiod=14)  # Calculate RSI-EMA
    df['Volume'] = df['Volume'] # Volume

    df.dropna(inplace=True) # Remove NULL values

    return df



def calculate_pnl(data, profit_target_pct, stop_loss_pct, trade_size):
    trades = []
    position = 0  # 1 for long, -1 for short, 0 for no position
    entry_price = 0
    profits = []

    for i in range(len(data)):
        if position == 0:
            if data['Signal'].iloc[i] > 0:
                position = 1
                entry_price = data['Close'].iloc[i]
            elif data['Signal'].iloc[i] < 0:
                position = -1
                entry_price = data['Close'].iloc[i]
        elif position == 1:
            if data['Close'].iloc[i] >= entry_price * (1 + profit_target_pct / 100) or \
               data['Close'].iloc[i] <= entry_price * (1 - stop_loss_pct / 100):
                
                pnl = (data['Close'].iloc[i] - entry_price) * trade_size / entry_price
                profits.append(pnl)
                data.at[data.index[i], 'PnL'] = pnl

                trades.append((entry_price, data['Close'].iloc[i], position, pnl))
                position = 0
        elif position == -1:
            if data['Close'].iloc[i] <= entry_price * (1 - profit_target_pct / 100) or \
               data['Close'].iloc[i] >= entry_price * (1 + stop_loss_pct / 100):
                
                pnl = (entry_price - data['Close'].iloc[i]) * trade_size / entry_price
                profits.append(pnl)
                data.at[data.index[i], 'PnL'] = pnl

                trades.append((entry_price, data['Close'].iloc[i], position, pnl))
                position = 0
        


    with open('trades.csv', 'w', newline='') as f:
        fields = ['entry', 'exit', 'pos']
        # writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer = csv.writer(f)
        # writer.writeheader()
        writer.writerows(list(trades))

    return sum(profits)


def plot(plt, df, graph_title):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['Close'], marker='^', color='g', label='Buy Signal')
    plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['Close'], marker='v', color='r', label='Sell Signal')
    plt.title('Buy and Sell Signals on AMD Historical Data')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.savefig("%s.png"%graph_title)
    print("Graph Plotted")