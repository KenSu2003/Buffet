import csv
def calculate_profitability(data, profit_target_pct, stop_loss_pct, trade_size):
    trades = []
    position = 0  # 1 for long, -1 for short, 0 for no position
    entry_price = 0

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
                trades.append((entry_price, data['Close'].iloc[i], position))
                position = 0
        elif position == -1:
            if data['Close'].iloc[i] <= entry_price * (1 - profit_target_pct / 100) or \
               data['Close'].iloc[i] >= entry_price * (1 + stop_loss_pct / 100):
                trades.append((entry_price, data['Close'].iloc[i], position))
                position = 0

    profits = []
    for entry, exit, pos in trades:
        if pos == 1:
            profits.append((exit - entry) * trade_size / entry)
        elif pos == -1:
            profits.append((entry - exit) * trade_size / entry)


    with open('trades.csv', 'w', newline='') as f:
        fields = ['entry', 'exit', 'pos']
        # writer = csv.DictWriter(csvfile, fieldnames=fields)
        writer = csv.writer(f)
        # writer.writeheader()
        writer.writerows(list(trades))
     

    # f = open("trades.txt", "w")
    # for trade in trades:
    #     f.write(list(trade))
    # f.close()

    return sum(profits)


def plot(plt, df):
    plt.figure(figsize=(14, 7))
    plt.plot(df.index, df['Close'], label='Close Price', color='blue')
    plt.scatter(df[df['Signal'] > 0].index, df[df['Signal'] > 0]['Close'], marker='^', color='g', label='Buy Signal')
    plt.scatter(df[df['Signal'] < 0].index, df[df['Signal'] < 0]['Close'], marker='v', color='r', label='Sell Signal')
    plt.title('Buy and Sell Signals on AMD Historical Data')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.show()