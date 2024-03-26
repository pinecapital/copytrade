from ScripCodeConverter import ScripConverter


csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
converter = ScripConverter(csv_url)

fyers_symbol = "NSE:BANKNIFTY24MAR46700CE"
scrip_code = converter.convert_symbol(fyers_symbol)

