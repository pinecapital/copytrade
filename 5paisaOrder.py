# first step to login
import json
from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange
import pyotp
from py5paisa.order import  Exchange
import logging
logging.basicConfig(level=logging.DEBUG)
# Read the JSON file
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)

# Access the credentials from the JSON data
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

# Generate TOTP using the secret key
totp_pin = pyotp.TOTP(totp_secret_key).now()

cred={
    "APP_NAME":appname,
    "APP_SOURCE":appsource,
    "USER_ID":userid,
    "PASSWORD":password,
    "USER_KEY":userkey,
    "ENCRYPTION_KEY":enckey
    }

client = FivePaisaClient(cred=cred)
client.get_totp_session(clientcode,totp_pin,pin)

print(client.access_token)
# client.place_order(OrderType='B',Exchange='N',ExchangeType='C', ScripData = "IDEA_EQ", Qty=1, Price=0)
# Placing order in 5paisa: OrderType=B, Exchange=N, ExchangeType=C, ScriptData=IDEA_EQ, Qty=1, Price=13.4, IsIntraday=True, StopLossPrice=None
client.place_order(OrderType='B',Exchange='N',ExchangeType='C', ScripData = "IDEA_EQ", Qty=1, Price=13.4,IsIntraday=False,StoplossPrice=None)

# #Using Scrip Data :-
# client.place_order(OrderType='B',Exchange='N',ExchangeType='C', ScriptData = "IDEA_EQ", Qty=1, Price=260)
# #Sample For SL order (for order to be treated as SL order just pass StopLossPrice)
# client.place_order(OrderType='B',Exchange='N',ExchangeType='C', ScriptData = "IDEA_EQ", Qty=1, Price=350, IsIntraday=False, StopLossPrice=345)
# #Derivative Order
# client.place_order(OrderType='B',Exchange='N',ExchangeType='D', ScriptData = "NIFTY 21 Dec 2023 CE 21300.00", Qty=50, Price=1.5)
