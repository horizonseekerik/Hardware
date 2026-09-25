import urllib.request
import json
import sys

def get_prices(region="centralindia", skus=None):
    if skus is None:
        skus = ["Standard_F16s_v2", "Standard_D16s_v5", "Standard_D8s_v5", "Standard_F8s_v2", "Standard_D4s_v5"]
    
    print(f"{'VM SKU':<22} | {'Region':<14} | {'Price / Hour':<14} | {'Est. 100M Cost (15-20 min)'}")
    print("-" * 75)
    
    for sku in skus:
        filter_str = f"armRegionName eq '{region}' and serviceName eq 'Virtual Machines' and priceType eq 'Consumption' and contains(armSkuName, '{sku}')"
        encoded_filter = urllib.parse.quote(filter_str)
        url = f"https://prices.azure.com/api/retail/prices?$filter={encoded_filter}"
        
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req) as resp:
                data = json.loads(resp.read().decode('utf-8'))
                items = [
                    it for it in data.get('Items', [])
                    if 'Spot' not in it.get('meterName', '')
                    and 'Low Priority' not in it.get('meterName', '')
                    and it.get('armSkuName') == sku
                ]
                if items:
                    it = items[0]
                    price = float(it['retailPrice'])
                    curr = it['currencyCode']
                    cost_100m = price * 0.33  # ~20 min is 0.33 hr
                    print(f"{sku:<22} | {region:<14} | {price:.4f} {curr}/hr | ~{cost_100m:.3f} {curr}")
                else:
                    print(f"{sku:<22} | {region:<14} | N/A (Not Listed) | N/A")
        except Exception as e:
            print(f"{sku:<22} | {region:<14} | Error: {e}")

if __name__ == "__main__":
    reg = sys.argv[1] if len(sys.argv) > 1 else "centralindia"
    get_prices(reg)
