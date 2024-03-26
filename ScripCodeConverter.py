import re
import re
import io
from io import StringIO
import csv
import requests
from datetime import datetime, timedelta, date
import pandas as pd

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
            # equity_symbol = symbol.split(':')[1].replace('-', '_')
                    # Extract the equity symbol (e.g., "IDEA" from "NSE:IDEA-EQ")
            equity_symbol = symbol.split(':')[1].split('-')[0]
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
