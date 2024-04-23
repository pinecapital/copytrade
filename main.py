import pyotp
import json
from py5paisa import FivePaisaClient
import pyotp
from fyers_apiv3.FyersWebsocket import order_ws
from fyersTokengenerate import generate_token
import logging 
import calendar

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


import calendar

def last_wednesday(year, month):
    """Find the last Wednesday of a given month."""
    total_days = calendar.monthrange(year, month)[1]
    for day in range(total_days, 0, -1):
        if calendar.weekday(year, month, day) == calendar.WEDNESDAY:
            return day
    return None  # In case no Wednesday is found

def convert_symbol(symbol):
    """Converts stock symbols between formats and generates detailed descriptors."""
    if not symbol.startswith("NSE:"):
        raise ValueError("Symbol must start with 'NSE:'")

    main_part = symbol[4:]  # Remove 'NSE:'
    month_to_num = {"JAN": 1, "FEB": 2, "MAR": 3, "APR": 4, "MAY": 5, "JUN": 6,
                    "JUL": 7, "AUG": 8, "SEP": 9, "OCT": 10, "NOV": 11, "DEC": 12}

    # Attempt to determine the format by length and content analysis
    try:
        # Determine the script name based on known patterns
        if main_part.startswith("BANKNIFTY"):
            scrip_name = "BANKNIFTY"
            name_length = 9
        elif main_part.startswith("NIFTY"):
            scrip_name = "NIFTY"
            name_length = 5
        else:
            raise ValueError("Unsupported scrip name.")

        # Try parsing as new format first
        if any(m in main_part for m in month_to_num):
            # New format like 'BANKNIFTY24MAY49500CE'
            year = "20" + main_part[name_length:name_length+2]
            month_abbr = main_part[name_length+2:name_length+5].upper()
            month = month_to_num.get(month_abbr)
            if month is None:
                raise ValueError(f"Invalid month abbreviation: {month_abbr}")
            strike_price = int(main_part[name_length+5:name_length+10])
            option_type = main_part[name_length+10:]
            day = last_wednesday(int(year), month)
        else:
            # Old format like 'NIFTY2450222000CE'
            year = "20" + main_part[name_length:name_length+2]
            month = int(main_part[name_length+2:name_length+3])
            day = int(main_part[name_length+3:name_length+5])
            strike_price = int(main_part[name_length+5:name_length+10])
            option_type = main_part[name_length+10:]
        
        if day is None:
            raise ValueError("Invalid date found in symbol.")

    except ValueError as e:
        print(f"Error parsing symbol: {e}")
        return str(e)

    # Format the output string
    month_name = calendar.month_abbr[month]
    formatted_date = f"{day:02d} {month_name} {year}"
    formatted_strike_price = f"{strike_price:.2f}"
    scrip_data = f"{scrip_name} {formatted_date} {option_type} {formatted_strike_price}_{year}{month:02d}{day:02d}_{option_type}_{strike_price}"

    return scrip_data


def onOrder(message):
    logging.info(f"Order Response: {message}")
    order = message.get('orders', {})
    # Get the orderNumStatus from the order

    if order.get('status') == 4:  # Check if it's a new order 4 for market close, 6 for new 
        fyers_symbol = order.get('symbol')
        logging.info(f"fyers symbol: {fyers_symbol}")
        # Convert to 5paisa ScripData
        scrip_data = convert_symbol(fyers_symbol)

        if scrip_data:
            for userid, client_data in clients.items():
                client = client_data['client']
                qty = client_data['qty']

                order_type = 'B' if order.get('side') == 1 else 'S'
                exchange = 'N'  # Assuming NSE
                exchange_type = 'C' if '_EQ' in scrip_data else 'D'  # Assuming Cash for EQ and Derivative otherwise
                # qty = order.get('qty')
                price = order.get('limitPrice', 0)  # Assuming 0 for market orders
                stopPrice = order.get('stopPrice', 0)  # Assuming 0 for market orders
                logging.info(f"Placing order in 5paisa: OrderType={order_type}, Exchange={exchange}, ExchangeType={exchange_type}, ScripCode={scrip_data}, Qty={qty}, Price={price}, StopPrice={stopPrice}")

                try:
                    # Use ScripCode instead of ScripData
                    response = client.place_order(OrderType=order_type, Exchange=exchange, ExchangeType=exchange_type,
                                                ScripData=str(scrip_data), Qty=int(qty), Price=float(price),
                                                IsIntraday=True, StoplossPrice=float(stopPrice))
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
