from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest, StockLatestQuoteRequest, CryptoBarsRequest, StockBarsRequest
from alpaca.common.exceptions import APIError
import os, pandas as pd

APCA_API_KEY_ID = "ALPACA-KEY"
APCA_API_SECRET_KEY = "ALPACA-SECRET-KEY"

trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
crypto_client = CryptoHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)
stock_client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

def close_position(symbol):
    symbol = symbol.replace('/','')
    trading_client.close_position(symbol)

def get_open_position(symbol):
    symbol = symbol.replace('/','')
    try:
        return trading_client.get_open_position(symbol)
    except APIError as e:
        if 'position does not exist' in str(e):
            print("**** The position does not exist. ****")
        else:
            print(f"An API error occurred: {e}")
        return None

def get_buy_sell(order):
    if order.side == 'long': return 1
    elif order.side == 'short': return -1
    else: return 0

def get_balance():
    account = trading_client.get_account()
    return float(account.equity)

def set_order(symbol,crypto_or_stock, long_short,ORDER_SIZE,order_limit=False,limit_price=0):
    if long_short == 'long':
        side=OrderSide.BUY
    elif long_short =='short':
        side=OrderSide.SELL
    else:
        print("long_short has to be \"long\" or \"short\" cannot be %s"%long_short)
        return 0

    # Limit order
    if order_limit: 
        limit_order_data = LimitOrderRequest(
                        symbol=symbol,
                        limit_price=limit_price,
                        notional=ORDER_SIZE,
                        side=side,
                        time_in_force=TimeInForce.GTC
                    )

        limit_order = trading_client.submit_order(
                        order_data=limit_order_data
                    )
        return limit_order
    
    # Market order
    else:   

        if crypto_or_stock == "crypto":
            multisymbol_request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
            latest_multisymbol_quotes = crypto_client.get_crypto_latest_quote(multisymbol_request_params)
        elif crypto_or_stock == "stock":
            multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
            latest_multisymbol_quotes = stock_client.get_stock_latest_quote(multisymbol_request_params)

        latest_ask_price = latest_multisymbol_quotes[symbol].ask_price

        qty = abs(ORDER_SIZE/latest_ask_price)    # for trading stock

        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty,
                            side=side,
                            # time_in_force=TimeInForce.DAY
                            time_in_force='gtc'
                            )
        
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
        # print(market_order.failed_at)   # need to move this to the crypto_paper_trading
        return market_order

def get_all_orders(symbol):
    request_params = GetOrdersRequest(symbol=symbol,status=QueryOrderStatus.CLOSED)
    orders = trading_client.get_orders(filter=request_params)
    orders_df = pd.DataFrame(orders)
    title = 'orders.csv'
    filepath = f"./data/{title}"
    os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure the directory for the graph_title record exists
    orders_df.to_csv(filepath)
    return orders_df

# ———————————————————————— TESTING ————————————————————————

# print(set_order('BTC/USD', 'crypto', 'long',1000,order_limit=False,limit_price=0))