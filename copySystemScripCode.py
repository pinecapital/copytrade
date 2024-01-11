from time import sleep
import pyotp
import json
from urllib.parse import parse_qs, urlparse
import warnings
import pandas as pd
import json
from py5paisa import FivePaisaClient
import pyotp
from fyers_apiv3.FyersWebsocket import order_ws

from ScripCodeConverter import ScripConverter, convert_to_5paisa_symbol

from fyersTokengenerate import generate_token
#logging.basicConfig(level=logging.DEBUG)

pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import base64


with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

client1 = config_data['client1']
appname = client1['appname']
appsource = client1['appsource']
userid = client1['userid']
password = client1['password']
userkey = client1['userkey']
enckey = client1['enckey']
clientcode = client1['clientcode']
pin = client1['pin']
totp_secret_key = client1['totp']

totp_pin = pyotp.TOTP(totp_secret_key).now()

cred={
    "APP_NAME":appname,
    "APP_SOURCE":appsource,
    "USER_ID":userid,
    "PASSWORD":password,
    "USER_KEY":userkey,
    "ENCRYPTION_KEY":enckey
    }

global client
client= FivePaisaClient(cred=cred)
client.get_totp_session(clientcode,totp_pin,pin)

access_token, client_id = generate_token()

csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
converter = ScripConverter(csv_url)

def onOrder(message):
    global client
    print("Order Response:", message)
    order = message.get('orders', {})

    if order.get('status') == 4:  # Check if it's a new order
        fyers_symbol = order.get('symbol')
        print(f"fyers symbol:{fyers_symbol}")
        # Convert to 5paisa ScripCode
        scrip_code = converter.convert_symbol(fyers_symbol)

        if scrip_code:
            order_type = 'B' if order.get('side') == 1 else 'S'
            exchange = 'N'  # Assuming NSE
            exchange_type = 'C' if '-EQ' in fyers_symbol else 'D'  # Assuming Cash for EQ and Derivative otherwise
            qty = order.get('qty')
            price = order.get('limitPrice', 0)  # Assuming 0 for market orders
            is_intraday = order.get('productType') == 'INTRADAY'

            print(f"Placing order in 5paisa: OrderType={order_type}, Exchange={exchange}, ExchangeType={exchange_type}, ScripCode={scrip_code}, Qty={qty}, Price={price}, IsIntraday={is_intraday}")

            try:
                # Use ScripCode instead of ScripData
                response = client.place_order(OrderType=order_type, Exchange=exchange, ExchangeType=exchange_type,
                                              ScripCode=int(scrip_code), Qty=int(qty), Price=float(price),
                                              IsIntraday=bool(is_intraday), StoplossPrice=0)
                print(f"Order response from 5paisa: {response}")
            except Exception as e:
                print(f"Error placing order in 5paisa: {e}")
        else:
            print(f"Unsupported symbol format for {fyers_symbol}")

        print(f"Order placement attempted in 5paisa for {scrip_code}")


def onerror(message):
    print("Error:", message)
def onclose(message):
    print("Connection closed:", message)
def onopen():
    data_type = "OnOrders"

    fyers.subscribe(data_type=data_type)
    fyers.keep_running()
access_token = f"{client_id}:{access_token}"
fyers = order_ws.FyersOrderSocket(
    access_token=access_token,
    write_to_file=False,
    log_path="",
    on_connect=onopen,
    on_close=onclose,
    on_error=onerror,
    on_orders=onOrder,
)

fyers.connect()
