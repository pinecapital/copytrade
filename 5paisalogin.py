# first step to login
import json
from py5paisa import FivePaisaClient
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

