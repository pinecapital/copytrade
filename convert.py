import re


def convert_symbol(symbol):
    # Check if the symbol follows the first format (e.g., NSE:IDEA-EQ)
    if '-EQ' in symbol:
        return symbol.split(':')[1].replace('-', '_')

    # Check if the symbol follows the second format (e.g., NSE:NIFTY23D2121300CE)
    match = re.match(r'NSE:(BANKNIFTY|FINNIFTY|NIFTY)(\d{2})([A-Z])(\d{2})(\d+)(CE|PE)', symbol)
    if match:
        index_name, year, month_code, date, strike_price, option_type = match.groups()

        # Convert year
        year = '20' + year

        # Convert month code
        month_codes = {'F': 'Jan', 'G': 'Feb', 'H': 'Mar', 'J': 'Apr', 'K': 'May', 'M': 'Jun',
                       'N': 'Jul', 'Q': 'Aug', 'U': 'Sep', 'V': 'Oct', 'X': 'Nov', 'D': 'Dec'}
        month = month_codes.get(month_code.upper())

        # Format strike price
        strike_price = f'{int(strike_price):.2f}'

        return f'{index_name} {date} {month} {year} {option_type} {strike_price}'

    return "Invalid format"


# Example usage
print(convert_symbol("NSE:IDEA-EQ"))
print(convert_symbol("NSE:NIFTY23D2116800CE"))
