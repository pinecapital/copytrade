import pandas as pd
import requests
import os
from datetime import datetime, timedelta

def download_csv(url, local_path):
    """
    Download a CSV file from a URL and save it to a local path, only if it's not already present.
    """
    if not os.path.exists(local_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(local_path, 'w') as file:
                file.write(response.text)
        else:
            raise Exception(f"Failed to download file: Status code {response.status_code}")
    else:
        print(f"File already exists: {local_path}")

def last_thursday(year, month):
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
def format_symbol(symbol_data):
    """
    Formats the symbol into the desired string for searching.
    """
    # print("Original Symbol Data:", symbol_data)  # Debugging

    if symbol_data[7:9].isalpha():  # First format: e.g., NIFTY24FEB21500CE
        year = "20" + symbol_data[5:7]
        month_str = datetime.strptime(symbol_data[7:10], '%b').strftime('%b')
        last_thursday_day = last_thursday(int(year), datetime.strptime(month_str, '%b').month)
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
def get_script_code(symbol, local_csv_path):
    """
    Return the ScriptCode for a given symbol, reading from a local CSV file.
    """
    # Read CSV from local file
    scrip_master_df = pd.read_csv(local_csv_path)
    if ":" in symbol: 
        parts = symbol.split(':')
        if len(parts) == 2:
            formatted_symbol = format_symbol(parts[1])
            # Search for the ScriptCode
            script_code = scrip_master_df[scrip_master_df['FullName'].str.contains(formatted_symbol, case=False, na=False)]['ScripCode']
            return script_code.values[0] if not script_code.empty else None
        else:
            return None
    else:
        formatted_symbol = format_symbol(symbol)
        # Search for the ScriptCode
        script_code = scrip_master_df[scrip_master_df['FullName'].str.contains(formatted_symbol, case=False, na=False)]['ScripCode']
        return script_code.values[0] if not script_code.empty else None

    # Example usage
csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
local_csv_path = "local_scrip_master.csv"

# Download CSV to local if not present
download_csv(csv_url, local_csv_path)

# Get ScriptCode
script_code = get_script_code("NSE:NIFTY24FEB21500CE", local_csv_path)
sc = get_script_code("NIFTY2411621500CE", local_csv_path)
print(script_code)
print(sc)
