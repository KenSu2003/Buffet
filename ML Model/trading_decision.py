
def make_trade_decision(df, model):
    X = df[['RSI', 'MACD', 'MACD_signal', 'BB_upper', 'BB_middle', 'BB_lower']].values
    prediction = model.predict(X[-1].reshape(1, -1))
    return 'BUY' if prediction >= 0.5 else 'SELL'

# Example trade decision for a specific date
# trade_date = '2020-01-18'
# df_trade = fetch_data(symbol, trade_date, (pd.to_datetime(trade_date) + pd.Timedelta(days=1)).strftime('%Y-%m-%d'))
# df_trade = add_technical_indicators(df_trade)
# decision = make_trade_decision(df_trade, model)
# print(f"Trade decision on {trade_date}: {decision}")
