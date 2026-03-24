# Bloomberg-Style Financial Terminal

A terminal-based real-time market data dashboard with Bloomberg-style aesthetics.

## Quick Start

```bash
python3 bloomberg_terminal.py
```

Press `Ctrl+C` to exit. Type `help` for commands.

---

## Features

### Core Features
- **Real-time market data** from free APIs (no API keys required)
- **Bloomberg-style UI** with black background and amber/green/red colors
- **Instant keyboard response** using curses library
- **Clear error states** - shows "NO DATA" when APIs fail

### Trading Features
- **Spot Trading** - market and limit orders on Binance (requires API keys)
- **Futures Trading** - leveraged long/short positions (requires API keys)
- **Trade History** - record and view all your buys/sells with persistent storage

### Analysis Features
- **Price Charts** - ASCII charts for historical price visualization
- **Asset Comparison** - compare performance of two assets over time
- **Market Heat Map** - visual overview of top gainers and losers
- **Fear & Greed Index** - crypto market sentiment indicator

### Productivity Features
- **Price Alerts** - get notified when prices hit targets
- **Watchlist** - track your favorite assets
- **Economic Calendar** - upcoming market-moving events
- **News Reader** - read full articles in terminal
- **Sentiment Analysis** - AI-powered news sentiment

---

## Codebase Architecture

The entire application is in a single file: `bloomberg_terminal.py` (~4000 lines). Here's how it's organized:

```
┌─────────────────────────────────────────────────────────────────┐
│                    CODEBASE STRUCTURE                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  1. IMPORTS & CONFIGURATION (Lines 1-700)                       │
│     ├── Standard library imports                                │
│     ├── API_ENDPOINTS dict - all API configurations             │
│     └── COLOR constants - terminal color scheme                 │
│                                                                 │
│  2. DATA FETCHING FUNCTIONS (Lines 700-1000)                    │
│     ├── get_crypto_prices()      - Binance API                  │
│     ├── get_metals_prices()      - Gold-API                     │
│     ├── get_forex_rates()        - Frankfurter API              │
│     ├── get_oil_price()          - FRED API                     │
│     ├── get_stock_prices()       - Yahoo Finance                │
│     ├── get_quick_prices()       - Aggregates all prices        │
│     └── get_all_real_data()      - Async data fetcher           │
│                                                                 │
│  3. FEATURE FUNCTIONS (Lines 1000-1500)                         │
│     ├── get_fear_greed_index()   - Crypto sentiment             │
│     ├── add_alert() / get_alerts() / delete_alert()             │
│     ├── add_to_watchlist() / get_watchlist()                    │
│     ├── analyze_sentiment()      - News sentiment analysis      │
│     ├── get_market_heat_map()    - Market movers                │
│     └── get_economic_calendar()  - Upcoming events              │
│                                                                 │
│  4. TRADING FUNCTIONS (Lines 1500-2100)                         │
│     ├── Spot: spot_market_buy(), spot_limit_sell(), etc.        │
│     ├── Futures: futures_long(), futures_short(), etc.          │
│     ├── record_trade() / get_trade_history()                    │
│     └── Binance API signing & authentication                    │
│                                                                 │
│  5. NEWS FUNCTIONS (Lines 2100-2400)                            │
│     ├── get_news()               - RSS feed fetcher             │
│     ├── fetch_full_article()     - Article content extractor    │
│     └── Article content cleaning & ad filtering                 │
│                                                                 │
│  6. CHART FUNCTIONS (Lines 2400-2700)                           │
│     ├── get_price_history()      - CoinGecko historical data    │
│     ├── generate_chart_lines()   - ASCII chart generator        │
│     └── generate_comparison_chart()                             │
│                                                                 │
│  7. TERMINAL CLASS (Lines 2700-4200)                            │
│     ├── __init__()               - Initialize state             │
│     ├── render()                 - Main dashboard               │
│     ├── render_heat_map()        - Heat map view                │
│     ├── render_alerts()          - Alerts view                  │
│     ├── render_watchlist()       - Watchlist view               │
│     ├── render_calendar()        - Calendar view                │
│     ├── render_news()            - News view                    │
│     ├── render_chart()           - Chart view                   │
│     ├── process_command()        - Command handler              │
│     └── handle_input()           - Keyboard handler             │
│                                                                 │
│  8. MAIN ENTRY POINT (Lines 4200-end)                           │
│     └── curses.wrapper(main)     - Start application            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Key Classes and Functions

| Component | Purpose | Location |
|-----------|---------|----------|
| `BloombergTerminal` | Main application class | Line ~2700 |
| `API_ENDPOINTS` | All API configurations | Line ~50 |
| `COLOR_*` constants | Terminal colors | Line ~695 |
| `get_quick_prices()` | Fetch all market data | Line ~950 |
| `process_command()` | Handle user commands | Line ~3377 |
| `handle_input()` | Keyboard events | Line ~4031 |

### Data Flow

```
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   APIs       │────▶│  get_quick_prices│────▶│  self.data dict │
│  (External)  │     │  (Aggregator)    │     │  (In-memory)    │
└──────────────┘     └──────────────────┘     └─────────────────┘
                                                       │
                                                       ▼
┌──────────────┐     ┌──────────────────┐     ┌─────────────────┐
│   Terminal   │◀────│    render()      │◀────│  Format prices  │
│   Display    │     │  (Draw to screen)│     │  for display    │
└──────────────┘     └──────────────────┘     └─────────────────┘
```

### Adding a New Feature

1. **Add data function** (if needed) in section 3:
```python
def get_my_data() -> Dict:
    """Fetch data from API"""
    # Implementation
    return data
```

2. **Add render method** in `BloombergTerminal` class:
```python
def render_my_feature(self):
    """Render my feature view"""
    self.screen.clear()
    # Draw UI
    self.screen.refresh()
```

3. **Add command handler** in `process_command()`:
```python
elif parts[0] == "myfeature":
    self.view_mode = "myfeature"
```

4. **Add view mode check** in `render()`:
```python
if self.view_mode == "myfeature":
    self.render_my_feature()
    return
```

---

## Database Files

| File | Purpose | Schema |
|------|---------|--------|
| `trades.db` | Trade history | `trades(id, symbol, side, quantity, price, total, timestamp)` |
| `alerts.db` | Price alerts | `alerts(id, symbol, target_price, condition, created_at, triggered)` |
| `watchlist.db` | User watchlist | `watchlist(id, symbol, added_at, notes)` |

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
├── bloomberg_terminal.py   # Main application (~4000 lines)
├── test_terminal.py        # Test suite
├── trades.db               # SQLite: trade history
├── alerts.db               # SQLite: price alerts
├── watchlist.db            # SQLite: user watchlist
├── trade_history.csv       # CSV backup of trades
├── README.md               # This file (architecture + usage)
├── USAGE.md                # Detailed usage guide
├── SHORTCUTS.md            # Quick reference
└── requirements.txt        # Dependencies (standard lib only)
```

---

## Testing

```bash
python3 test_terminal.py
```

Tests:
- API connectivity (Binance, Gold-API, Frankfurter, etc.)
- Price formatting
- Terminal class structure
- No mock data verification

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
| Article not loading | Some sites block scraping, press `O` to open in browser |

---

## License

MIT License - Free to use and modify.
