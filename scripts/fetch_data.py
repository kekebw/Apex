import urllib.request
import json
import time
import os
import ssl
import re

ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE

HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
}

def fetch_cnn():
        try:
                    url = 'https://feargreedmeter.com/'
                    req = urllib.request.Request(url, headers=HEADERS)
                    res = urllib.request.urlopen(req, context=ctx).read().decode('utf-8')
                    match = re.search(r'is currently at (\d+)', res)
                    if match:
                                    return int(match.group(1))
        except Exception as e:
                    print(f"Fetch failed: {e}")
                return None

def fetch_yahoo(symbol, range_str='1y', interval_str='1d'):
        try:
                    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?range={range_str}&interval={interval_str}"
                    req = urllib.request.Request(url, headers=HEADERS)
                    res = urllib.request.urlopen(req, context=ctx).read()
                    return json.loads(res.decode('utf-8'))
except Exception as e:
        print(f"Error fetching Yahoo {symbol}: {e}")
        return None

def main():
        print("Starting data fetch...")
    result = {
                'timestamp': int(time.time()),
                'fear_and_greed': fetch_cnn(),
                'indices': {}
    }
    print(f"Fear & Greed Index: {result['fear_and_greed']}")

    indices = {
                'DAX': '^GDAXI',
                'DOW': '^DJI',
                'SP500': '^GSPC',
                'NIKKEI': '^N225',
                'MSCI_CHINA': 'MCHI'
    }

    ranges = {
                '1D': ('1d', '5m'),
                '1W': ('5d', '60m'),
                '1M': ('1mo', '1d'),
                '1Y': ('1y', '1d')
    }

    for key, symbol in indices.items():
                print(f"Fetching {key}...")
                result['indices'][key] = {}
                for r_name, (r_val, i_val) in ranges.items():
                                data = fetch_yahoo(symbol, r_val, i_val)
                                if data and not data['chart']['error']:
                                                    try:
                                                                            times = data['chart']['result'][0]['timestamp']
                                                                            closes = data['chart']['result'][0]['indicators']['quote'][0]['close']

                    series = []
                    for i in range(len(times)):
                                                if closes[i] is not None:
                                                                                series.append({
                                                                                                                    'time': times[i],
                                                                                                                    'price': round(float(closes[i]), 2)
                                                                                    })
                                                                        result['indices'][key][r_name] = series
except Exception as e:
                    print(f"Parse error for {key} {r_name}: {e}")
            time.sleep(1)

    os.makedirs('data', exist_ok=True)
    with open('data/market.json', 'w') as f:
                json.dump(result, f)
    print("Data successfully written to data/market.json")

if __name__ == '__main__':
        main()
