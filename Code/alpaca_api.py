from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest, GetOrdersRequest
from alpaca.trading.enums import OrderSide, TimeInForce, QueryOrderStatus
from alpaca.data.historical import CryptoHistoricalDataClient, StockHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest, StockLatestQuoteRequest, CryptoBarsRequest, StockBarsRequest
from alpaca.common.exceptions import APIError
import os, pandas as pd

APCA_API_KEY_ID = "PKC0I8RIJHZDQZTI5OGX"
APCA_API_SECRET_KEY = "yzsEuNmXfwDMNqHP1Jg1Q5njGAuuL0CPhwRURO4P"

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
    return account

def set_order(symbol,crypto_or_stock, long_short,order_size,order_limit=False,limit_price=0):
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
                        notional=order_size,
                        side=side,
                        time_in_force=TimeInForce.GTC
                    )

        limit_order = trading_client.submit_order(
                        order_data=limit_order_data
                    )
        return limit_order
    
    # Market order
    else:   
        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            notional=order_size,
                            side=side,
                            time_in_force='gtc'
                            )
        print(market_order_data.notional)
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
        
        return market_order

def get_all_orders(symbol):
    request_params = GetOrdersRequest(symbol=symbol,status=QueryOrderStatus.CLOSED)
    orders = trading_client.get_orders(filter=request_params)
    orders_df = pd.DataFrame(orders)
    return orders_df

# ———————————————————————— TESTING ————————————————————————

# all_filled_orders = get_all_orders('BTC/USD')
# title = 'orders_15min_31days.csv'
# filepath = f"./data/{title}"
# os.makedirs(os.path.dirname(filepath), exist_ok=True) # Ensure the directory for the graph_title record exists
# all_filled_orders.to_csv(filepath)

# print(set_order('BTC/USD', 'crypto', 'long',1000,order_limit=False,limit_price=0))


'''
    Need to review the trade algorithm
'''