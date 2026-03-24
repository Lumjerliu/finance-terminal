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
| `Enter` | Execute command / Open selected article |
| `ESC` | Clear command / Go back |
| `Backspace` | Delete last character |
| `H` | Toggle trade history view |

### News View Controls

| Key | Action |
|-----|--------|
| `↑`/`↓` | Navigate articles / Scroll article content |
| `PgUp`/`PgDn` | Scroll article by page |
| `Enter` | Open selected article (full content) |
| `O` | Open article in browser |
| `Esc` | Back to news list / Main view |
| `1-9` | Open article by number |

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

### New Features Commands

| Command | Description | Example |
|---------|-------------|---------|
| `heatmap` | Show market heat map with Fear & Greed | `heatmap` |
| `alerts` | View all price alerts | `alerts` |
| `alert <sym> <price> above/below` | Set price alert | `alert BTC 100000 above` |
| `delalert <id>` | Delete alert | `delalert 1` |
| `watchlist` | View your watchlist | `watchlist` |
| `watch <sym>` | Add to watchlist | `watch BTC` |
| `unwatch <sym>` | Remove from watchlist | `unwatch BTC` |
| `calendar` | Show economic calendar | `calendar` |
| `sentiment` | Show market sentiment analysis | `sentiment` |

### News Commands

| Command | Description | Example |
|---------|-------------|---------|
| `news <category>` | View news headlines | `news business`, `news crypto` |
| `reddit <sub>` | View Reddit posts | `reddit stocks`, `reddit crypto` |
| `open <#>` | Read article in terminal | `open 5` |
| `view <#>` | Same as open (read in terminal) | `view 3` |
| `browser <#>` | Open article in browser | `browser 5` |
| `O` key | Open selected article in browser | (press O) |

### News Categories

| Category | Description |
|----------|-------------|
| `business` | Business news (CNBC, Yahoo Finance) |
| `stocks` | Stock market news |
| `crypto` | Cryptocurrency news (CoinTelegraph, CoinDesk) |
| `politics` | Political news |
| `world` | World news |

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
║  NEW FEATURES                                                 ║
║  heatmap       → Market heat map + Fear & Greed               ║
║  alerts        → View price alerts                            ║
║  alert <sym> <price> above/below → Set alert                  ║
║  watchlist     → View your watchlist                          ║
║  watch <sym>   → Add to watchlist                             ║
║  calendar      → Economic calendar                            ║
║  sentiment     → Market sentiment analysis                    ║
╠══════════════════════════════════════════════════════════════╣
║  Ctrl+C        → Exit terminal                                ║
║  Enter         → Execute command                              ║
║  ESC           → Clear input / Go back                        ║
╚══════════════════════════════════════════════════════════════╝
```
