import json
from py5paisa import FivePaisaClient
import pyotp
import logging
from multiprocessing import Pool

logging.basicConfig(level=logging.DEBUG)

def create_session_for_client(client_data):
    appname = client_data['appname']
    appsource = client_data['appsource']
    userid = client_data['userid']
    password = client_data['password']
    userkey = client_data['userkey']
    enckey = client_data['enckey']
    clientcode = client_data['clientcode']
    pin = client_data['pin']
    totp_secret_key = client_data['totp']

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

    print(f"Access token for {userid}: {client.access_token}")

if __name__ == '__main__':
    # Read the JSON file
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    # Create a session for each client in parallel
    with Pool() as p:
        p.map(create_session_for_client, config_data.values())