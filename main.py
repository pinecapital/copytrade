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

from fyers_apiv3.FyersWebsocket import order_ws


def onOrder(message):
    print("Order Response:", message)


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
