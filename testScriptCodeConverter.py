from ScripCodeConverter import ScripConverter


csv_url = "https://openapi.5paisa.com/VendorsAPI/Service1.svc/ScripMaster/segment/All"
converter = ScripConverter(csv_url)

fyers_symbol = "NSE:IDEA-EQ"
scrip_code = converter.convert_symbol(fyers_symbol)

print(f"5paisa scrip code: {scrip_code}")