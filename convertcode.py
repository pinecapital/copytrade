import csv
import requests
import re
import io

class ScripConverter:
    def __init__(self, csv_url):
        self.csv_url = csv_url
        self.csv_data = self.download_csv(csv_url)

    def download_csv(self, url):
        response = requests.get(url)
        response.raise_for_status()  # Ensure the download was successful
        return response.text

    def get_csv_reader(self):
        return csv.DictReader(io.StringIO(self.csv_data))

    def find_scrip_code(self, formatted_symbol):
        csv_reader = self.get_csv_reader()
        for row in csv_reader:
            if row['Name'] == formatted_symbol and row['Exch'] == 'N' and row['ExchType'] == 'D':
                return row['ScripCode']
        return None

    def convert_symbol(self, symbol):
        if '-EQ' in symbol:
            return symbol.split(':')[1].replace('-', '_')
        # Check if the symbol follows the second format (e.g., NSE:NIFTY23D2121300CE)
        match = re.match(r'NSE:(BANKNIFTY|FINNIFTY|NIFTY)(\d{2})([A-Z])(\d{2})(\d+)(CE|PE)', symbol)
        if match:
            index_name, year, month_code, date, strike_price, option_type = match.groups()
            year = '20' + year
            month_codes = {'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 'K': 'May', 'M': 'Jun',
                           'N': 'Jul', 'Q': 'Aug', 'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'D': 'Dec'}
            month = month_codes.get(month_code.upper())
            strike_price = f'{int(strike_price):.2f}'
            formatted_symbol = f'{index_name} {date} {month} {year} {option_type} {strike_price}'
            scrip_code = self.find_scrip_code(formatted_symbol)
            return scrip_code or formatted_symbol

        return "Invalid format"

# Example usage
csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
converter = ScripConverter(csv_url)
print(converter.convert_symbol("NSE:NIFTY23D2116800CE"))

