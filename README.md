# Bloomberg-Style Financial Terminal

A terminal-based real-time market data dashboard with Bloomberg-style aesthetics.

## Quick Start

```bash
python3 bloomberg_terminal.py
```

## Features

- **Real-time market data** from free APIs (no API keys required)
- **Bloomberg-style UI** with black background and amber/green/red colors
- **Instant keyboard response** using curses library
- **Clear error states** - shows "NO DATA" when APIs fail
- **Easy API swapping** - all APIs configured in one place
- **Trade History** - record and view all your buys/sells with persistent storage
- **Price Charts** - ASCII charts for historical price visualization
- **Asset Comparison** - compare performance of two assets over time

---

## API Configuration

All APIs are configured at the top of `bloomberg_terminal.py` in the **API CONFIGURATION** section. You can easily swap to premium APIs by changing the endpoints.

### Current Free APIs (No Key Required)

| Data Type | Provider | Free Endpoint | Premium Alternative |
|-----------|----------|---------------|---------------------|
| **Crypto** | Binance | `https://api.binance.com/api/v3/ticker/24hr` | CoinGecko Pro, Coinbase Pro |
| **Gold/Silver** | Gold-API | `https://api.gold-api.com/price/{symbol}` | Metals-API, GoldAPI.io |
| **Forex** | Frankfurter | `https://api.frankfurter.app/latest` | Open Exchange Rates, Fixer |
| **Oil** | FRED | `https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO` | OilPriceAPI, EIA API |
| **Stocks** | Yahoo Finance | `https://query1.finance.yahoo.com/v8/finance/chart/{symbol}` | Alpha Vantage, IEX Cloud |

### How to Swap APIs

1. Open `bloomberg_terminal.py`
2. Find the **API CONFIGURATION** section (near line 20)
3. Change the `API_ENDPOINTS` dictionary:

```python
# Example: Switch to premium CoinGecko API
API_ENDPOINTS = {
    'crypto': {
        'provider': 'coingecko',
        'base_url': 'https://api.coingecko.com/api/v3',
        'api_key': 'YOUR_API_KEY_HERE',
    },
    # ... other APIs
}
```

### Premium API Options

| Provider | Free Tier | Paid From | Best For |
|----------|-----------|-----------|----------|
| **Alpha Vantage** | 25 calls/day | $50/mo | Stocks, Forex |
| **IEX Cloud** | 50k messages/mo | $9/mo | US Stocks |
| **CoinGecko Pro** | 50 calls/min | $129/mo | Crypto |
| **Metals-API** | 100 requests/mo | $15/mo | Gold, Silver |
| **Fixer** | 100 requests/mo | $10/mo | Forex |
| **OilPriceAPI** | Trial | $29/mo | Oil, Energy |
| **Polygon.io** | 5 calls/min | $199/mo | Real-time stocks |

---

## API Details

### 1. Crypto (Binance) - Working

**Free Endpoint:**
```
GET https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "lastPrice": "71000.00",
  "priceChangePercent": "1.5"
}
```

**Symbols:** BTC, ETH, SOL, XRP, DOGE, ADA, AVAX, LINK

**Premium Alternatives:**
- **CoinGecko Pro**: More coins, historical data
- **Coinbase Pro**: Direct exchange data
- **CryptoCompare**: Aggregated prices

---

### 2. Gold and Silver (Gold-API) - Working

**Free Endpoint:**
```
GET https://api.gold-api.com/price/XAU  # Gold
GET https://api.gold-api.com/price/XAG  # Silver
GET https://api.gold-api.com/price/HG   # Copper
```

**Response:**
```json
{
  "name": "Gold",
  "price": 4423.70,
  "symbol": "XAU"
}
```

**Premium Alternatives:**
- **Metals-API**: 170+ metals, historical data - metals-api.com
- **GoldAPI.io**: Real-time spot prices - goldapi.io

---

### 3. Forex (Frankfurter) - Working

**Free Endpoint:**
```
GET https://api.frankfurter.app/latest?from=USD&to=EUR,GBP,JPY
```

**Response:**
```json
{
  "base": "USD",
  "rates": {
    "EUR": 0.86,
    "GBP": 0.75,
    "JPY": 158.55
  }
}
```

**Pairs:** EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD

**Premium Alternatives:**
- **Open Exchange Rates**: 200+ currencies - openexchangerates.org
- **Fixer.io**: European Central Bank rates - fixer.io
- **CurrencyLayer**: Real-time rates - currencylayer.com

---

### 4. Oil (FRED) - Sometimes Slow

**Free Endpoint:**
```
GET https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO
```

Returns CSV with daily WTI prices.

**Premium Alternatives:**
- **EIA API**: Official US energy data - eia.gov/opendata
- **OilPriceAPI**: Real-time oil prices - oilpriceapi.com
- **Quandl**: Historical commodity data - quandl.com

---

### 5. Stocks (Yahoo Finance) - Rate Limited

**Free Endpoint:**
```
GET https://query1.finance.yahoo.com/v8/finance/chart/AAPL?interval=1d&range=1d
```

**Note:** Yahoo Finance may rate-limit. Consider premium alternatives for production.

**Premium Alternatives:**
- **Alpha Vantage**: Official free tier, paid options - alphavantage.co
- **IEX Cloud**: Real-time US stock data - iexcloud.io
- **Polygon.io**: Real-time and historical - polygon.io
- **Finnhub**: Free tier available - finnhub.io

---

## Adding Your Own API

1. Create a new function in the API section:

```python
def get_my_custom_prices() -> Dict:
    """Fetch prices from your custom API"""
    data = {}
    
    url = API_ENDPOINTS['my_api']['base_url'] + '/prices'
    api_key = API_ENDPOINTS['my_api'].get('api_key', '')
    
    # Add API key to headers if needed
    headers = {'Authorization': f'Bearer {api_key}'} if api_key else {}
    result = fetch_url_with_headers(url, headers)
    
    if result:
        for item in result['prices']:
            data[item['symbol']] = {
                'price': float(item['price']),
                'change': float(item['change']),
                'pct': float(item['changePercent']),
                'name': item['name']
            }
    
    return data
```

2. Add to `get_quick_prices()` or `get_all_real_data()`

3. Add your API config:

```python
API_ENDPOINTS = {
    # ... existing APIs
    'my_api': {
        'provider': 'my_provider',
        'base_url': 'https://api.myservice.com',
        'api_key': os.environ.get('MY_API_KEY', ''),
    },
}
```

---

## Environment Variables

For premium APIs, use environment variables:

```bash
# Add to ~/.zshrc or ~/.bashrc
export BINANCE_API_KEY="your_key"
export BINANCE_API_SECRET="your_secret"
export ALPHAVANTAGE_API_KEY="your_key"
export POLYGON_API_KEY="your_key"
```

Then in code:

```python
import os
API_ENDPOINTS = {
    'stocks': {
        'api_key': os.environ.get('ALPHAVANTAGE_API_KEY', ''),
    },
}
```

---

## File Structure

```
finance-terminal/
├── bloomberg_terminal.py   # Main application
├── test_terminal.py        # Test suite
├── trades.db               # SQLite database for trade history
├── trade_history.csv       # CSV backup of all trades
├── README.md               # This file
├── SHORTCUTS.md            # Keyboard shortcuts
└── requirements.txt        # Python dependencies (standard lib only)
```

---

## Requirements

- Python 3.7+
- curses (built-in on macOS/Linux)
- Internet connection

No external dependencies required - uses only Python standard library.

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "NO DATA" everywhere | Check internet connection, wait 5 seconds |
| API rate limited | Wait a few minutes, or switch to premium API |
| Stocks not loading | Yahoo Finance may be rate-limited, try later |
| Oil not loading | FRED is sometimes slow, wait or use premium API |
| Terminal not rendering | Ensure terminal is at least 80x30 characters |

---

## Commands

| Command | Description |
|---------|-------------|
| `help` | Show available commands |
| `view <sym>` | Focus on a symbol |
| `refresh` | Force data refresh |
| `back` | Return to main view |
| `chart <sym> <days>` | Show price chart for last N days |
| `chart <sym> <start> <end>` | Show price chart for date range (YYYY-MM-DD) |
| `compare <sym1> <sym2> <days>` | Compare two assets over N days |
| `compare <sym1> <sym2> <start> <end>` | Compare two assets for date range |
| `buy <sym> <qty>` | Record a buy trade at current market price |
| `sell <sym> <qty>` | Record a sell trade at current market price |
| `history` or `trades` | View trade history |
| `delete <id>` | Delete a trade by ID |

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| `H` | Toggle trade history view |
| `Esc` | Return to main view |
| `Ctrl+C` | Exit terminal |

## Price Charts & Comparisons

View historical price data with ASCII charts directly in your terminal.

### Single Asset Chart

```
COMMAND> chart BTC 30
[Shows BTC price chart for last 30 days]

COMMAND> chart ETH 2024-01-01 2024-03-01
[Shows ETH price from Jan 1 to Mar 1, 2024]
```

### Compare Two Assets

```
COMMAND> compare BTC ETH 30
[Shows percentage change comparison for last 30 days]

COMMAND> compare BTC ETH 2024-01-01 2024-06-01
[Shows comparison for date range]
```

### Supported Assets for Charts

Charts work for crypto assets via CoinGecko API:
- BTC, ETH, SOL, XRP, DOGE, ADA, AVAX, LINK, DOT, MATIC, LTC, UNI

## Trade History

Your trades are stored in two places:
1. **SQLite Database** (`trades.db`) - Primary storage, supports queries
2. **CSV File** (`trade_history.csv`) - Backup, easy to open in Excel

### Example Usage

```
COMMAND> buy BTC 0.5
BUY 0.5 BTC @ $85,000.00 = $42,500.00 (ID: 1)

COMMAND> sell ETH 2
SELL 2 ETH @ $3,200.00 = $6,400.00 (ID: 2)

COMMAND> history
[Shows trade history table]

COMMAND> delete 1
Deleted trade #1
```

Press `Ctrl+C` to exit.

---

## Testing

```bash
python3 test_terminal.py
```

---

## License

MIT License - Free to use and modify.
