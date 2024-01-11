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

appid = config['alok']['appid']

secret_key = config['alok']['secid']
client_id = config['alok']['client_id']
redirect_uri = "https://127.0.0.1/"
PIN = config['alok']['PIN']
TOTP_KEY = config['alok']['totp']
FY_ID = client_id
grant_type = "authorization_code"
response_type = "code"
state = "sample"


### Connect to the sessionModel object here with the required input parameters
appSession = fyersModel.SessionModel(client_id = appid, redirect_uri = redirect_uri,response_type=response_type,state=state,secret_key=secret_key,grant_type=grant_type)

# ## Make  a request to generate_authcode object this will return a login url which you need to open in your browser from where you can get the generated auth_code 
generateTokenUrl = appSession.generate_authcode()


print((generateTokenUrl)) 