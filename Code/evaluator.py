from alpaca_api import GetOrdersRequest, QueryOrderStatus, trading_client
symbol = 'BTC/USD'
print("Creating Order Request")
request_params = GetOrdersRequest(symbol=symbol,status=QueryOrderStatus.CLOSED)
print("Getting Orders")
orders = trading_client.get_orders(filter=request_params)
keys = orders.keys
print("Keys",keys)