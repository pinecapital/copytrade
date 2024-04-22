## Login from fyers , copy the real time trades to 5paisa 

## steps 
1. get the api key 
2. get the realtime order update of fyers , subscribe to websocket 
3. convert the instrument 
4. place order


## How to run 
1. when first setup, run the activate 
2. put the script in a crontab that would rerun the script everday-


### Scrip Data conversion

# complete 


### adding stoploss functions

# response 
12:28:22 - root - INFO - Order Response: {'s': 'ok', 'orders': {'clientId': 'YA02826', 'id': '24042200209586', 'exchOrdId': '1500000104413065', 'qty': 15, 'remainingQuantity': 15, 'limitPrice': 247, 'stopPrice': 247.5, 'type': 1, 'fyToken': '101124042467522', 'exchange': 10, 'segment': 11, 'symbol': 'NSE:BANKNIFTY24APR47800CE', 'instrument': 14, 'offlineOrder': False, 'orderDateTime': '22-Apr-2024 12:28:22', 'orderValidity': 'DAY', 'productType': 'INTRADAY', 'side': -1, 'status': 6, 'source': 'W', 'ex_sym': 'BANKNIFTY', 'description': '24 Apr 24 47800 CE', 'orderNumStatus': '24042200209586:6'}}

## normal order response 


