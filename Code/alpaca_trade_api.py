from alpaca.trading.client import TradingClient
from alpaca.trading.requests import MarketOrderRequest, LimitOrderRequest
from alpaca.trading.enums import OrderSide, TimeInForce

from alpaca.data.historical import StockHistoricalDataClient
from alpaca.data.requests import StockLatestQuoteRequest

APCA_API_KEY_ID = "PKDSUFSDD8XOZZC309LK"
APCA_API_SECRET_KEY = "araI1T7gB3rsXErEanFI9QwIdyQeVE8XUgGOMtey"

trading_client = TradingClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY, paper=True)
price_client = StockHistoricalDataClient(APCA_API_KEY_ID, APCA_API_SECRET_KEY)


def get_balance():
    account = trading_client.get_account()
    return account.equity

# preparing orders
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
                        time_in_force=TimeInForce.FOK
                    )

        limit_order = trading_client.submit_order(
                        order_data=limit_order_data
                    )
        
    else:   # Market order
        
        multisymbol_request_params = StockLatestQuoteRequest(symbol_or_symbols=symbol)
        latest_multisymbol_quotes = price_client.get_stock_latest_quote(multisymbol_request_params)
        latest_ask_price = latest_multisymbol_quotes[symbol].ask_price  # returns 0 when market is closed

        qty = round(abs(ORDER_SIZE/latest_ask_price))
        print(qty)

        market_order_data = MarketOrderRequest(
                            symbol=symbol,
                            qty=qty,
                            side=side,
                            time_in_force=TimeInForce.DAY
                            )
        
        market_order = trading_client.submit_order(
                        order_data=market_order_data
                    )
    
    