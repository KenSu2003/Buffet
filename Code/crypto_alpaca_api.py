from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from alpaca.data.historical import CryptoHistoricalDataClient
from alpaca.data.requests import CryptoLatestQuoteRequest

from alpaca.common.exceptions import APIError

import time

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
                            # time_in_force=TimeInForce.DAY
                            time_in_force='gtc'
                            )
        
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
    
        return market_order

####### Testing #######
# symbol = 'BTC/USD'
# POSITION_SIZE = 50000
# signal = -1
# trade_log = 1

# ####### Determine Order Size and Execute Order #######
# open_order = get_open_position(symbol)       # GETTING POSITON NOT ORDER NEED TO REEVALUATE
# order_size = abs(POSITION_SIZE*signal)

# # Check if there is an Active (Open) Order
# if open_order != None:
#     open_order_id = open_order.asset_id
#     open_order_side = get_buy_sell(open_order)

#     current_balance = float(open_order.qty)*float(open_order.market_value)    # order size = availabe asset
#     account_balance = get_balance()     # order size = entire account availabe USD balance

#     if open_order_side < 0: # For Active Short Position
        
#         if signal>0: 
#             if order_size >= account_balance: # Close Long Position
#                 order_size = account_balance
#                 if trade_log: print(f"Reducing Order Size to {order_size}.")
#                 if trade_log: print(f"Closing Short Position {open_order_id}")
#                 close_position(symbol)   # if its an active long order close it
#             else:
#                 if trade_log: print(f"Opening Long Order {open_order_id}")
#                 if trade_log: print(f"Reducing Short Position by ${order_size}")
#                 set_order(symbol,'long',order_size)
#         elif signal<0:
#             order_size = current_balance
#             if trade_log: print(f"Increasing Short Position {order_size}")
#             set_order(symbol,'short',order_size)
#     elif open_order_side > 0:   # For Active Long Position        
#         if signal<0: 
#             if order_size >= current_balance: # Close Long Position
#                 order_size = current_balance
#                 if trade_log: print(f"Closing Long Position {open_order_id}")
#                 close_position(symbol)  # if its an active short order close it
#             else:
#                 if trade_log: print(f"Opening Short Order {open_order_id}")
#                 if trade_log: print(f"Reducing Long Position by ${abs(order_size)}")
#                 set_order(symbol,'short',order_size)
#         elif signal>0:
#             if order_size>account_balance: order_size = account_balance
#             if trade_log: print(f"Increasing Long Position {order_size}")
#             set_order(symbol,'long',order_size)
# else:
#     if signal > 0:
#         if trade_log: print(f"Opening a new Long ${order_size} Order")
#         set_order(symbol,'long',order_size)
#     elif signal < 0:
#         if trade_log: print("Insufficient Fund.")
#     else:
#         if trade_log: print("No trades made.")