
import yfinance as yf
import pandas as pd


def fetch_data(symbol, start_date, end_date, interval='1d'):
    data = yf.download(symbol, start=start_date, end=end_date, interval=interval)
    data.dropna(inplace=True) # Remove NULL values
    return data

# Example usage:
symbol = 'AMD'
start_date = '2018-01-01'
end_date = '2023-01-01'
df = fetch_data(symbol, start_date, end_date)
