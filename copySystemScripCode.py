import configparser
from fyers_apiv3 import fyersModel
from datetime import datetime, timedelta, date
from time import sleep
import os
import pyotp
import requests
import json
import math
import pytz
from urllib.parse import parse_qs, urlparse
import warnings
import pandas as pd
import json
from py5paisa import FivePaisaClient
from py5paisa.order import Order, OrderType, Exchange
import pyotp
from py5paisa.order import  Exchange
from fyers_apiv3.FyersWebsocket import order_ws
import re
from io import StringIO

import logging
#logging.basicConfig(level=logging.DEBUG)

pd.set_option('display.max_columns', None)
warnings.filterwarnings('ignore')
import base64

config = configparser.ConfigParser()
config.read('config.ini')

appid = config['master']['appid']

secret_key = config['master']['secid']
client_id = config['master']['client_id']

redirect_uri = "https://127.0.0.1/"
PIN = config['master']['PIN']
TOTP_KEY = config['master']['totp']
FY_ID = client_id
grant_type = "authorization_code"
response_type = "code"
state = "sample"

#5paisa integration
# Access the credentials from the JSON data
# Read the JSON file
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

global client
client= FivePaisaClient(cred=cred)
client.get_totp_session(clientcode,totp_pin,pin)


def getEncodedString(string):
    string = str(string)
    base64_bytes = base64.b64encode(string.encode("ascii"))
    return base64_bytes.decode("ascii")


URL_SEND_LOGIN_OTP = "https://api-t2.fyers.in/vagator/v2/send_login_otp_v2"
res = requests.post(url=URL_SEND_LOGIN_OTP, json={"fy_id": getEncodedString(FY_ID), "app_id": "2"}).json()
#
if datetime.now().second % 30 > 27: sleep(5)
URL_VERIFY_OTP = "https://api-t2.fyers.in/vagator/v2/verify_otp"
res2 = requests.post(url=URL_VERIFY_OTP,
                     json={"request_key": res["request_key"], "otp": pyotp.TOTP(TOTP_KEY).now()}).json()

ses = requests.Session()
URL_VERIFY_OTP2 = "https://api-t2.fyers.in/vagator/v2/verify_pin_v2"
payload2 = {"request_key": res2["request_key"], "identity_type": "pin", "identifier": getEncodedString(PIN)}
res3 = ses.post(url=URL_VERIFY_OTP2, json=payload2).json()

ses.headers.update({
    'authorization': f"Bearer {res3['data']['access_token']}"
})

TOKENURL = "https://api-t1.fyers.in/api/v3/token"
payload3 = {"fyers_id": FY_ID,
            "app_id": appid[:-4],
            "redirect_uri": redirect_uri,
            "appType": "100", "code_challenge": "",
            "state": "None", "scope": "", "nonce": "", "response_type": "code", "create_cookie": True}
#
res3 = ses.post(url=TOKENURL, json=payload3).json()
print(res3)
url = res3['Url']
parsed = urlparse(url)
auth_code = parse_qs(parsed.query)['auth_code'][0]

grant_type = "authorization_code"

response_type = "code"

session = fyersModel.SessionModel(
    client_id=appid,
    secret_key=secret_key,
    redirect_uri=redirect_uri,
    response_type=response_type,
    grant_type=grant_type
)

session.set_token(auth_code)

response = session.generate_token()

access_token = response['access_token']



def convert_to_5paisa_symbol(fyers_symbol):
    if '-EQ' in fyers_symbol:
        return fyers_symbol.split(':')[1].replace('-', '_')

    match = re.match(r'NSE:(BANKNIFTY|FINNIFTY|NIFTY)(\d{2})([A-Z])(\d{2})(\d+)(CE|PE)', fyers_symbol)
    if match:
        index_name, year, month_code, date, strike_price, option_type = match.groups()
        year = '20' + year
        month_codes = {'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 'K': 'May', 'M': 'Jun', 'N': 'Jul', 'Q': 'Aug',
                       'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'D': 'Dec'}
        month = month_codes.get(month_code.upper())
        formatted_date = f"{date} {month} {year}"
        strike_price = float(strike_price)
        return f"{index_name} {formatted_date} {option_type} {strike_price:.2f}"

    return None
import csv
import requests
import re
import io

class ScripConverter:
    def __init__(self, csv_url):
        self.csv_data = self.download_csv(csv_url)
        self.scrip_master_df = pd.read_csv(StringIO(self.csv_data))


    def download_csv(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Ensure the download was successful
        return response.text

    def get_csv_reader(self):
        return csv.DictReader(io.StringIO(self.csv_data))

    def last_thursday(self,year, month):
        """
        Find the last Thursday of a given month and year.
        """
        if month == 12:
            last_day = datetime(year + 1, 1, 1) - timedelta(days=1)
        else:
            last_day = datetime(year, month + 1, 1) - timedelta(days=1)

        weekday = last_day.weekday()
        if weekday < 3:  # Adjust for Mon, Tue, Wed
            last_day -= timedelta(days=weekday + 4)
        elif weekday > 3:  # Adjust for Fri, Sat, Sun
            last_day -= timedelta(days=weekday - 3)

        return last_day.day
    def format_symbol(self,symbol_data):
        """
        Formats the symbol into the desired string for searching.
        """
        # print("Original Symbol Data:", symbol_data)  # Debugging
        if symbol_data.startswith('NIFTY'):
            if symbol_data[7:9].isalpha():  # First format: e.g., NIFTY24FEB21500CE
                year = "20" + symbol_data[5:7]
                month_str = datetime.strptime(symbol_data[7:10], '%b').strftime('%b')
                last_thursday_day = self.last_thursday(int(year), datetime.strptime(month_str, '%b').month)
                strike_price = symbol_data[10:-2]
                option_type = symbol_data[-2:]

                # print("Year:", year, "Month:", month_str, "Day:", last_thursday_day, "Strike Price:", strike_price, "Option Type:", option_type)  # Debugging

                return f"{symbol_data[:5]} {last_thursday_day:02d} {month_str} {year} {option_type} {strike_price}.00"
            else:  # Second format: e.g., NIFTY2410421500CE
                year = "20" + symbol_data[5:7]
                month = int(symbol_data[7:8])
                day = int(symbol_data[8:10])
                strike_price = symbol_data[10:-2]
                option_type = symbol_data[-2:]
                month_str = datetime(int(year), month, 1).strftime('%b')  # Corrected line

                # print("Year:", year, "Month:", month_str, "Day:", day, "Strike Price:", strike_price, "Option Type:", option_type)  # Debugging

                return f"{symbol_data[:5]} {day:02d} {month_str} {year} {option_type} {strike_price}.00"
        if symbol_data.startswith('BANKNIFTY'): #NSE:BANKNIFTY24JAN48000CE
            if symbol_data[11:13].isalpha():
                year = "20" + symbol_data[9:11]
                month_str = datetime.strptime(symbol_data[11:14], '%b').strftime('%b')
                last_thursday_day = self.last_thursday(int(year), datetime.strptime(month_str, '%b').month)
                strike_price = symbol_data[14:-2]
                option_type = symbol_data[-2:]

                # print("Year:", year, "Month:", month_str, "Day:", last_thursday_day, "Strike Price:", strike_price, "Option Type:", option_type)  # Debugging

                return f"{symbol_data[:9]} {last_thursday_day:02d} {month_str} {year} {option_type} {strike_price}.00"
            else:  # Second format: e.g., BANKNIFTY2412548000CE
                year = "20" + symbol_data[9:11]
                month = int(symbol_data[11:12])
                day = int(symbol_data[12:14])
                strike_price = symbol_data[14:-2]
                option_type = symbol_data[-2:]
                month_str = datetime(int(year), month, 1).strftime('%b')
                return f"{symbol_data[:9]} {day:02d} {month_str} {year} {option_type} {strike_price}.00"

    def find_scrip_code(self, formatted_symbol, exchange, exch_type):
        csv_reader = self.get_csv_reader()
        for row in csv_reader:
            if row['Name'].strip() == formatted_symbol and row['Exch'] == exchange and row['ExchType'] == exch_type:
                return row['ScripCode']
        return None

    def convert_symbol(self, symbol):
        # Standard equity format (e.g., NSE:IDEA-EQ)
        if '-EQ' in symbol:
            equity_symbol = symbol.split(':')[1].replace('-', '_')
            return self.find_scrip_code(equity_symbol, 'B', 'C')
        else:
            if ":" in symbol: 
                parts = symbol.split(':')
                if len(parts) == 2:
                    formatted_symbol = self.format_symbol(parts[1])
                    # Search for the ScriptCode
                    script_code = self.scrip_master_df[self.scrip_master_df['FullName'].str.contains(formatted_symbol, case=False, na=False)]['ScripCode']
                    return script_code.values[0] if not script_code.empty else None
                else:
                    return None
            else:
                formatted_symbol = self.format_symbol(symbol)
                # Search for the ScriptCode
                script_code = self.scrip_master_df[self.scrip_master_df['FullName'].str.contains(formatted_symbol, case=False, na=False)]['ScripCode']
                return script_code.values[0] if not script_code.empty else None


    

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
