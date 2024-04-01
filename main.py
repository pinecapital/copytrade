import pyotp
import json
from py5paisa import FivePaisaClient
import pyotp
from fyers_apiv3.FyersWebsocket import order_ws
from ScripCodeConverter import ScripConverter
from fyersTokengenerate import generate_token
import logging 
logging.basicConfig(filename='app.log', filemode='w', format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%H:%M:%S', level=logging.INFO)
# Global dictionary to store FivePaisaClient instances
clients = {}
with open('config.json', 'r') as config_file:
    config_data = json.load(config_file)
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
    qty = client_data['qty']
    clientsymbol = client_data['clientsymbol']

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
    clients[userid] = {'client': client, 'qty': qty}

    logging.info(f"Access token for {userid}: {client.access_token}")


access_token, client_id = generate_token()

csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
converter = ScripConverter(csv_url)


def onOrder(message):
    logging.info(f"Order Response: {message}")
    order = message.get('orders', {})
    # Get the orderNumStatus from the order

    if order.get('status') == 6:  # Check if it's a new order # change to 4 for testing
        fyers_symbol = order.get('symbol')
        logging.info(f"fyers symbol: {fyers_symbol}")
        # Convert to 5paisa ScripCode
        # scrip_code = converter.convert_symbol(fyers_symbol)
        # logging.info(f"5paisa scrip code: {scrip_code}")
        # Convert the Fyers symbol to the required equity symbol format
        # Extract the part after "NSE:" and replace '-' with '_'
        equity_symbol = fyers_symbol.split(':')[1].replace('-', '_')
        logging.info(f"Equity symbol: {equity_symbol}")

        if equity_symbol:
            for userid, client_data in clients.items():
                client = client_data['client']
                qty = client_data['qty']
                # Use clientsymbol if present, otherwise use the equity_symbol
                symbol_for_order = client_data.get('clientsymbol', '').strip() or equity_symbol

                order_type = 'B' if order.get('side') == 1 else 'S'
                exchange = 'N'  # Assuming NSE
                # exchange_type = 'C' if '-EQ' in fyers_symbol else 'D'  # Assuming Cash for EQ and Derivative otherwise
                exchange_type = 'C'
                # qty = order.get('qty')
                price = order.get('limitPrice', 0)  # Assuming 0 for market orders
                is_intraday = order.get('productType') == 'INTRADAY'

                logging.info(f"Placing order in 5paisa: OrderType={order_type}, Exchange={exchange}, ExchangeType={exchange_type}, ScripData={equity_symbol}, Qty={qty}, Price={price}, IsIntraday={is_intraday}")

                try:
                    # Use ScripCode instead of ScripData
                    response = client.place_order(OrderType=order_type, Exchange=exchange, ExchangeType=exchange_type,
                                                ScripData=str(symbol_for_order), Qty=int(qty), Price=float(price),
                                                IsIntraday=bool(is_intraday), StoplossPrice=0)
                    logging.info(f"Order response from 5paisa for {userid}: {response}")

                except Exception as e:
                    logging.error(f"Error placing order in 5paisa: {e}")
        else:
            logging.error(f"Unsupported symbol format for {fyers_symbol}")

        

def onerror(message):
    logging.error(f"Error: {message}")

def onclose(message):
    logging.info(f"Connection closed: {message}")
def onopen():
    data_type = "OnOrders"

    fyers.subscribe(data_type=data_type)
    fyers.keep_running()

if __name__ == '__main__':
    # Create a session for each client in parallel
    with open('config.json', 'r') as config_file:
        config_data = json.load(config_file)

    # Create a session for each client
    for client_data in config_data.values():
        create_session_for_client(client_data)
    
    access_token = f"{client_id}:{access_token}"
    fyers = order_ws.FyersOrderSocket(
        access_token=access_token,
        write_to_file=False,
        log_path="",
        reconnect=True,
        on_connect=onopen,
        on_close=onclose,
        on_error=onerror,
        on_orders=onOrder,
    )

    fyers.connect()
