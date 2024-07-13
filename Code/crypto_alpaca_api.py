from alpaca.trading.client import TradingClient
from alpaca.trading.requests import GetOrdersRequest
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

from alpaca.common.exceptions import APIError

import csv, pandas as pd


APCA_API_KEY_ID = "PKHR4PFM00KX8GGXP9EG"
APCA_API_SECRET_KEY = "QgH9zpwOkOodiP9LzRUMn2scmxJLd8QCnKUxpi25"

trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
price_client = CryptoHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)

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

def set_order(symbol,long_short,ORDER_SIZE,order_limit=False,limit_price=0):

    if long_short == 'long':
        side=OrderSide.BUY
    elif long_short =='short':
        side=OrderSide.SELL
    else:
        print("long_short has to be \"long\" or \"short\" cannot be %s"%long_short)
        return 0

    if order_limit: # Limit order
        
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
        
    else:   # Market order

        multisymbol_request_params = CryptoLatestQuoteRequest(symbol_or_symbols=symbol)
        latest_multisymbol_quotes = price_client.get_crypto_latest_quote(multisymbol_request_params)
        latest_ask_price = latest_multisymbol_quotes[symbol].ask_price

        qty = abs(ORDER_SIZE/latest_ask_price)    # for trading stock

        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty,
                            side=side,
                            time_in_force='gtc'
                            )
        
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
        print(market_order.failed_at)   # need to move this to the crypt_paper_trading
        return market_order

def get_all_orders(symbol):
    request_params = GetOrdersRequest(symbol=symbol,status=QueryOrderStatus.CLOSED)
    orders = trading_client.get_orders(filter=request_params)
    print(orders)
    orders_df = pd.DataFrame(orders)
    orders_df.to_csv('orders.csv')
    return orders_df