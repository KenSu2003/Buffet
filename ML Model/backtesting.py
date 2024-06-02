import datetime
import logging
from trading_decision import make_trade_decision
from data_preparation import fetch_data
from feature_engineering import add_technical_indicators
from model_training import create_features_labels, build_model
from tqdm import tqdm

# Configure logging
logging.basicConfig(level=logging.INFO)

def get_next_trading_day(symbol, date, max_attempts=5):
    # Adjust to the next available trading day
    for offset in range(1, max_attempts + 1):
        next_date = date + datetime.timedelta(days=offset)
        df = fetch_data(symbol, next_date.strftime('%Y-%m-%d'), (next_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
        if not df.empty:
            return next_date
    return None

def backtest(symbol, start_year, end_year, trade_day=None):
    results = []

    for year in tqdm(range(start_year, end_year), desc="Backtesting Progress"):
        start_date = datetime.datetime(year, 1, 17)
        end_date = datetime.datetime(year + 1, 1, 17)
        if trade_day:
            trade_date = datetime.datetime.strptime(trade_day, '%Y-%m-%d')
        else:
            trade_date = datetime.datetime(year + 1, 1, 18)

        # Fetch and prepare data for the entire year
        df_train = fetch_data(symbol, start_date.strftime('%Y-%m-%d'), end_date.strftime('%Y-%m-%d'))
        if df_train.empty:
            logging.warning(f"No training data for period {start_date} to {end_date}")
            continue

        df_train = add_technical_indicators(df_train)
        X_train, y_train = create_features_labels(df_train)

        # Train the model
        model = build_model(X_train.shape[1])
        model.fit(X_train, y_train, epochs=50, batch_size=32, verbose=0)

        # Make trade decision for the trade_date
        for attempt in range(5):
            df_trade = fetch_data(symbol, trade_date.strftime('%Y-%m-%d'), (trade_date + datetime.timedelta(days=1)).strftime('%Y-%m-%d'))
            if not df_trade.empty:
                break
            logging.warning(f"No trade data for date {trade_date}, adjusting to next trading day.")
            trade_date = trade_date + datetime.timedelta(days=1)
        else:
            logging.error(f"Failed to find trade data for date {trade_date}")
            continue

        df_trade = add_technical_indicators(df_trade)
        if df_trade.empty:
            logging.warning(f"Insufficient trade data after adding indicators for date {trade_date}")
            continue

        X_trade, _ = create_features_labels(df_trade)
        if len(X_trade) == 0:
            logging.warning(f"No valid data points for making trade decision on {trade_date}")
            continue

        decision = make_trade_decision(df_trade, model)
        
        results.append((trade_date.strftime('%Y-%m-%d'), decision))

    return results

# Example usage
trade_day = '2022-01-30'  # Specify the trade day here, or set to None to use default logic
backtest_results = backtest('AMD', 2019, 2023, trade_day)
for result in backtest_results:
    print(f"Date: {result[0]}, Decision: {result[1]}")
