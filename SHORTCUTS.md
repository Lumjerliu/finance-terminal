# Bloomberg Terminal - Shortcuts & Commands Guide

## Quick Start
```bash
python3 bloomberg_terminal.py
```

## Data Sources

| Asset Type | API | URL | Key Required |
|------------|-----|-----|--------------|
| **Crypto** (BTC, ETH, SOL, etc.) | Binance | api.binance.com | ❌ No |
| **Gold, Silver, Copper** | Gold-API.com | api.gold-api.com | ❌ No |
| **Forex** (EUR/USD, etc.) | Frankfurter.app | api.frankfurter.app | ❌ No |
| **Oil (WTI)** | FRED | fred.stlouisfed.org | ❌ No |
| **Stocks** (AAPL, NVDA, etc.) | Yahoo Finance | query1.finance.yahoo.com | ❌ No* |

*Yahoo Finance may be rate-limited. All other APIs are reliable and free.

**Note**: Terminal shows "NO DATA" in red until APIs connect. Check the header for API status:
- **LIVE** = All APIs working
- **PARTIAL** = Some APIs working
- **ERROR** = APIs failing

## Keyboard Controls

| Key | Action |
|-----|--------|
| `Ctrl+C` | Exit terminal |
| `Enter` | Execute command |
| `ESC` | Clear current command |
| `Backspace` | Delete last character |

---

## Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show available commands | `help` |
| `view <symbol>` | View specific asset | `view btc`, `view aapl` |
| `back` | Return to main view | `back` |
| `refresh` | Force refresh prices | `refresh` |
| `bal` | Show account balance (requires Binance API) | `bal` |
| `buy <sym> <qty>` | Place buy order | `buy btc 0.1` |
| `sell <sym> <qty>` | Place sell order | `sell eth 1` |

---

## Display Sections

The terminal displays:

### ★ Market Spotlight (Top)
6 prominent boxes showing the most important prices:
- **Row 1**: BTC, ETH, SPX
- **Row 2**: Gold, Oil, EUR/USD

Shows **"NO DATA"** in red if API hasn't loaded that asset.

### Equities (12 stocks)
AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, JPM, V, WMT, DIS, NFLX

### Crypto (8 coins)
BTC, ETH, SOL, XRP, DOGE, ADA, AVAX, LINK

### Forex (6 pairs)
EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD

### Commodities (5)
OIL, GOLD, SILVER, NATGAS, COPPER

### Indices (5)
SPX, DJI, NDQ, VIX, RUT

---

## Color Scheme

| Color | Meaning |
|-------|---------|
| Amber/Yellow | Headers, borders, prompts |
| Green ▲ | Price gains |
| Red ▼ | Price losses |
| **Red "NO DATA"** | API hasn't loaded this asset |
| White | Normal text |
| Gray | Secondary info |

---

## Binance Trading (Optional)

To enable real trading, set environment variables:
```bash
export BINANCE_API_KEY="your-api-key"
export BINANCE_API_SECRET="your-api-secret"
```

---

## Error Handling

The terminal clearly shows when data is unavailable:
- **"NO DATA"** in red = That asset hasn't loaded yet
- **API: ERROR** in header = APIs are failing
- **API: PARTIAL** in header = Some APIs working
- **API: LIVE** in header = All APIs working

You can trust that any price shown is real data from APIs.

---

## Requirements

- Python 3.7+
- curses (built-in on macOS/Linux)
- Internet connection for API data

---

## Tips

1. Make your terminal window at least 80x30 characters
2. Use a dark-themed terminal for best appearance
3. Run in a real terminal (not inside an IDE)
4. The terminal requires an interactive TTY
5. If you see "NO DATA", wait a few seconds for APIs to connect

---

## Quick Reference

```
╔══════════════════════════════════════════════════════════════╗
║                    QUICK COMMANDS                             ║
╠══════════════════════════════════════════════════════════════╣
║  view <sym>    → Focus on symbol                              ║
║  refresh       → Force price refresh                          ║
║  buy <sym> <qty>   → Market buy                               ║
║  sell <sym> <qty>  → Market sell                              ║
║  bal           → Show balances                                ║
║  help          → Show commands                                ║
║  back          → Return to main view                          ║
╠══════════════════════════════════════════════════════════════╣
║  Ctrl+C        → Exit terminal                                ║
║  Enter         → Execute command                              ║
║  ESC           → Clear input                                  ║
╚══════════════════════════════════════════════════════════════╝
```
