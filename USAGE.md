# Bloomberg Terminal - Complete Usage Guide

This guide explains every feature of the Bloomberg-style financial terminal.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Dashboard](#main-dashboard)
3. [Commands Reference](#commands-reference)
4. [Price Charts](#price-charts)
5. [Asset Comparison](#asset-comparison)
6. [Trade History](#trade-history)
7. [Keyboard Shortcuts](#keyboard-shortcuts)
8. [Troubleshooting](#troubleshooting)

---

## Getting Started

### Starting the Terminal

```bash
cd finance-terminal
python3 bloomberg_terminal.py
```

### Exiting the Terminal

Press `Ctrl+C` to exit at any time.

---

## Main Dashboard

When you start the terminal, you will see the main dashboard with:

### Header Section
- Current date and time
- API connection status (LIVE, PARTIAL, or ERROR)
- Number of assets being tracked

### Market Spotlight
Six featured assets displayed in prominent boxes:
- **BTC** - Bitcoin
- **ETH** - Ethereum
- **SPX** - S&P 500 Index
- **GOLD** - Gold price
- **OIL** - Crude Oil (WTI)
- **EUR/USD** - Euro to Dollar exchange rate

Each box shows:
- Asset name
- Current price in USD
- Percentage change (green for gains, red for losses)

### Data Tables

1. **EQUITIES** - US Stocks (AAPL, MSFT, GOOGL, AMZN, TSLA, NVDA, META, JPM, V, WMT, DIS, NFLX)

2. **CRYPTO** - Cryptocurrencies (BTC, ETH, SOL, XRP, DOGE, ADA, AVAX, LINK)

3. **FOREX** - Currency pairs (EUR/USD, GBP/USD, USD/JPY, USD/CHF, AUD/USD, USD/CAD)

4. **COMMODITIES** - Raw materials (OIL, GOLD, SILVER, NATGAS, COPPER)

5. **INDICES** - Market indices (SPX, DJI, NDQ, VIX, RUT)

### Understanding the Display

| Symbol | Meaning |
|--------|---------|
| UP arrow | Price went up |
| DOWN arrow | Price went down |
| NO DATA | API failed or rate limited |
| LIVE | APIs working correctly |
| PARTIAL | Some APIs working |
| ERROR | APIs not responding |

---

## Commands Reference

Type commands at the `COMMAND>` prompt and press Enter.

### Navigation Commands

| Command | Description | Example |
|---------|-------------|---------|
| `help` | Show available commands | `help` |
| `view <symbol>` | Focus on a specific asset | `view BTC` |
| `back` | Return to main dashboard | `back` |
| `refresh` | Force update all prices | `refresh` |

### Chart Commands

| Command | Description | Example |
|---------|-------------|---------|
| `chart <sym> <days>` | Show price chart for last N days | `chart BTC 30` |
| `chart <sym> <start> <end>` | Show chart for date range | `chart ETH 2024-01-01 2024-03-01` |
| `compare <s1> <s2> <days>` | Compare two assets | `compare BTC ETH 30` |
| `compare <s1> <s2> <start> <end>` | Compare for date range | `compare BTC ETH 2024-01-01 2024-06-01` |

### Trade Commands

| Command | Description | Example |
|---------|-------------|---------|
| `buy <sym> <qty>` | Record a buy trade | `buy BTC 0.5` |
| `sell <sym> <qty>` | Record a sell trade | `sell ETH 2` |
| `history` | View all trades | `history` |
| `trades` | Same as history | `trades` |
| `delete <id>` | Delete a trade by ID | `delete 5` |

---

## Price Charts

### Viewing a Single Asset

**Show last 30 days:**
```
COMMAND> chart BTC 30
```

**Show last 7 days:**
```
COMMAND> chart ETH 7
```

**Show specific date range:**
```
COMMAND> chart BTC 2024-01-01 2024-03-31
```

### Understanding the Chart

The chart displays an ASCII visualization with:
- **Y-axis**: Price in USD
- **X-axis**: Date range
- **Block characters**: Show price level at each point

### Supported Assets for Charts

Charts work for cryptocurrencies via CoinGecko API:

| Symbol | Name |
|--------|------|
| BTC | Bitcoin |
| ETH | Ethereum |
| SOL | Solana |
| XRP | Ripple |
| DOGE | Dogecoin |
| ADA | Cardano |
| AVAX | Avalanche |
| LINK | Chainlink |
| DOT | Polkadot |
| MATIC | Polygon |
| LTC | Litecoin |
| UNI | Uniswap |

---

## Asset Comparison

### Comparing Two Assets

The comparison chart shows **percentage change** from the starting point, making it easy to see which asset performed better.

**Compare last 30 days:**
```
COMMAND> compare BTC ETH 30
```

**Compare specific period:**
```
COMMAND> compare BTC ETH 2024-01-01 2024-06-01
```

### Understanding Comparison Charts

- Different block characters represent each asset
- **0.0%** is the starting point (both begin here)
- **Positive**: Asset gained value
- **Negative**: Asset lost value

### Use Cases

1. **Which crypto performed better?**
   ```
   compare BTC ETH 90
   ```
   See which had better returns over 90 days.

2. **Compare during a market event:**
   ```
   compare BTC ETH 2024-03-01 2024-03-15
   ```
   See how they reacted during a specific period.

3. **Long-term comparison:**
   ```
   compare SOL ETH 365
   ```
   Full year comparison.

---

## Trade History

### Recording Trades

Trades are recorded at the **current market price** when you enter the command.

**Buy Example:**
```
COMMAND> buy BTC 0.5
BUY 0.5 BTC @ $85,000.00 = $42,500.00 (ID: 1)
```

**Sell Example:**
```
COMMAND> sell ETH 2
SELL 2 ETH @ $3,200.00 = $6,400.00 (ID: 2)
```

### Viewing Trade History

```
COMMAND> history
```

Or press `H` key anytime.

The history shows:
- **ID**: Trade identifier (for deletion)
- **Date/Time**: When the trade was recorded
- **Symbol**: Asset traded
- **Side**: BUY or SELL
- **Quantity**: Amount traded
- **Price**: Price per unit
- **Total**: Total value of trade

### Deleting a Trade

```
COMMAND> delete 5
Deleted trade #5
```

### Data Storage

Your trades are stored in two formats:

1. **SQLite Database** (`trades.db`)
   - Primary storage
   - Fast queries
   - Persistent across sessions

2. **CSV File** (`trade_history.csv`)
   - Human-readable backup
   - Can open in Excel/Sheets
   - Easy to export/share

---

## Keyboard Shortcuts

| Key | Action |
|-----|--------|
| H | Toggle trade history view |
| Esc | Return to main dashboard |
| Ctrl+C | Exit terminal |
| Enter | Execute command |
| Backspace | Delete character |

---

## Troubleshooting

### "NO DATA" Shows Everywhere

**Cause:** Internet connection issue or all APIs are rate-limited.

**Solutions:**
1. Check your internet connection
2. Wait 1-2 minutes for rate limit to reset
3. Run `refresh` command to retry

### Charts Not Loading

**Cause:** CoinGecko API rate limit (10-50 calls/minute for free tier).

**Solutions:**
1. Wait a minute and try again
2. Use smaller day ranges
3. Data is cached for 5 minutes - repeated calls are instant

### Stocks/Indices Show "NO DATA"

**Cause:** Yahoo Finance is rate-limited (unofficial API).

**Solutions:**
1. Wait a few minutes
2. Stocks are less critical - crypto/forex/commodities are more reliable

### Terminal Looks Glitchy

**Cause:** Terminal window too small.

**Solutions:**
1. Resize terminal to at least 80 columns x 30 rows
2. Maximize terminal window
3. Use a smaller font if needed

---

## Tips and Best Practices

### Efficient Chart Usage

1. **Use caching:** Once you view a chart, it is cached for 5 minutes
2. **Batch comparisons:** Load one chart, then compare - second asset loads faster
3. **Date ranges:** Use date ranges for precise historical analysis

### Trade Tracking

1. **Record immediately:** Record trades right after execution for accurate prices
2. **Use IDs:** Note trade IDs if you might need to delete later
3. **CSV backup:** The CSV file is your backup - do not delete it

### Performance Analysis

1. **Compare before buying:** Use `compare` to see which asset performed better
2. **Check trends:** Use `chart` with 90+ days to see long-term trends
3. **Spot volatility:** Short timeframes (7 days) show volatility better

---

## API Reference

The terminal uses free APIs that do not require keys:

| Data Type | Provider | Rate Limit |
|-----------|----------|------------|
| Crypto Prices | Binance | 1200 req/min |
| Crypto History | CoinGecko | 10-50 req/min |
| Forex | Frankfurter | Generous |
| Gold/Silver | Gold-API | 500 req/month |
| Oil | FRED | Generous |
| Stocks | Yahoo Finance | Rate limited |

### Upgrading to Premium

See `README.md` for premium API alternatives with higher limits.

---

## File Structure

```
finance-terminal/
├── bloomberg_terminal.py   # Main application
├── trades.db               # Your trade history (auto-created)
├── trade_history.csv       # CSV backup (auto-created)
├── README.md               # Project overview and API docs
├── USAGE.md                # This file
├── SHORTCUTS.md            # Quick reference
├── requirements.txt        # Dependencies (standard lib only)
└── test_terminal.py        # Test suite
```

---

## Getting Help

- Press `help` in the terminal for quick command reference
- Check `README.md` for API configuration
- Check this file for detailed usage

---

*Happy trading!*
