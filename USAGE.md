# Bloomberg Terminal - Complete Usage Guide

This guide explains every feature of the Bloomberg-style financial terminal.

---

## Table of Contents

1. [Getting Started](#getting-started)
2. [Main Dashboard](#main-dashboard)
3. [Commands Reference](#commands-reference)
4. [Price Charts](#price-charts)
5. [Asset Comparison](#asset-comparison)
6. [Spot Trading](#spot-trading)
7. [Futures Trading](#futures-trading)
8. [Trade History](#trade-history)
9. [Keyboard Shortcuts](#keyboard-shortcuts)
10. [Troubleshooting](#troubleshooting)

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

### Spot Trading Commands

| Command | Description | Example |
|---------|-------------|---------|
| `bal` | Show account balances | `bal` |
| `buy <sym> <qty>` | Market buy (or local record) | `buy BTC 0.01` |
| `buy <sym> <qty> <price>` | Limit buy order | `buy BTC 0.01 85000` |
| `sell <sym> <qty>` | Market sell (or local record) | `sell ETH 0.5` |
| `sell <sym> <qty> <price>` | Limit sell order | `sell ETH 0.5 3500` |
| `orders` | Show open spot orders | `orders` |
| `orders <sym>` | Show orders for symbol | `orders BTC` |
| `cancel <sym> <id>` | Cancel spot order | `cancel BTC 12345` |

### Futures Trading Commands

| Command | Description | Example |
|---------|-------------|---------|
| `long <sym> <qty>` | Open long position (1x leverage) | `long BTC 0.01` |
| `long <sym> <qty> <lev>` | Open long with leverage | `long BTC 0.01 10` |
| `short <sym> <qty>` | Open short position (1x leverage) | `short ETH 0.5` |
| `short <sym> <qty> <lev>` | Open short with leverage | `short ETH 0.5 5` |
| `close <sym>` | Close position for symbol | `close BTC` |
| `positions` | Show open futures positions | `positions` |
| `leverage <sym> <lev>` | Set leverage for symbol | `leverage BTC 20` |
| `orders -f` | Show open futures orders | `orders -f` |
| `cancel <sym> <id> -f` | Cancel futures order | `cancel BTC 12345 -f` |

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

## Spot Trading

### Setting Up Trading

To enable real trading on Binance, you need API keys:

1. **Create API Key**
   - Go to https://www.binance.com/en/my/settings/api-management
   - Click "Create API"
   - Enable "Enable Spot & Margin Trading"
   - Set IP whitelist for security

2. **Configure Keys**
   
   **Option A: Environment Variables (Recommended)**
   ```bash
   export BINANCE_API_KEY="your_api_key"
   export BINANCE_API_SECRET="your_secret_key"
   ```
   
   **Option B: Config File**
   Create `trading_config.py` in the terminal directory:
   ```python
   BINANCE_API_KEY = "your_api_key"
   BINANCE_API_SECRET = "your_secret_key"
   ```

3. **Security Notes**
   - NEVER commit API keys to git
   - Use IP whitelist restriction
   - Start with small amounts for testing
   - Consider using read-only keys first

### Checking Balance

```
COMMAND> bal
Spot USDT: $1,000.00 (locked: $0.00)
Futures USDT: $500.00 (avail: $500.00)
```

### Market Orders

Execute immediately at current market price.

**Buy (Spot):**
```
COMMAND> buy BTC 0.01
Executing BUY 0.01 BTCUSDT...
Order placed! ID: 12345678
```

**Sell (Spot):**
```
COMMAND> sell ETH 0.5
Executing SELL 0.5 ETHUSDT...
Order placed! ID: 12345679
```

### Limit Orders

Execute only at specified price or better.

**Limit Buy:**
```
COMMAND> buy BTC 0.01 85000
[Places buy order at $85,000 per BTC]
```

**Limit Sell:**
```
COMMAND> sell ETH 0.5 3500
[Places sell order at $3,500 per ETH]
```

### Viewing Open Orders

```
COMMAND> orders
BTCUSDT BUY 0.01 @ $85,000.00 | ID: 12345678
ETHUSDT SELL 0.5 @ $3,500.00 | ID: 12345679
```

### Canceling Orders

```
COMMAND> cancel BTC 12345678
Cancelled order #12345678
```

### Trading Without API Keys

If you don't have API keys configured, the terminal still works as a **trade journal**:

```
COMMAND> buy BTC 0.01
[LOCAL] BUY 0.01 BTCUSDT @ $87,000.00 = $870.00 (ID: 1)
```

This records the trade locally for tracking purposes.

---

## Futures Trading

Futures trading allows leverage (1x to 125x) and short positions.

### Enabling Futures

1. Enable "Enable Futures" in your Binance API settings
2. Transfer USDT to your futures account
3. Use futures-specific commands

### Opening Long Position

A long position profits when price goes UP.

```
COMMAND> long BTC 0.01 10
Opening long BTCUSDT x10...
Futures LONG placed! ID: 12345680
```

This opens a 10x leveraged long position.

### Opening Short Position

A short position profits when price goes DOWN.

```
COMMAND> short ETH 0.5 5
Opening short ETHUSDT x5...
Futures SHORT placed! ID: 12345681
```

This opens a 5x leveraged short position.

### Setting Leverage

Change leverage before or independently:

```
COMMAND> leverage BTC 20
BTCUSDT leverage set to 20x
```

### Viewing Positions

```
COMMAND> positions
BTCUSDT LONG 0.01 @ $87,000.00 | PnL: +$50.00
ETHUSDT SHORT 0.5 @ $3,200.00 | PnL: -$25.00
```

### Closing Positions

```
COMMAND> close BTC
Closing BTCUSDT position...
Position closed! Order ID: 12345682
```

### Futures Orders

View futures open orders:
```
COMMAND> orders -f
BTCUSDT BUY 0.01 @ $85,000.00 | ID: 12345680
```

Cancel futures order:
```
COMMAND> cancel BTC 12345680 -f
Cancelled order #12345680
```

### Risk Management

**IMPORTANT WARNINGS:**

1. **Leverage Risk**: Higher leverage = higher liquidation risk
   - 10x leverage liquidates at 10% price move against you
   - 100x leverage liquidates at 1% price move against you

2. **Liquidation**: If price hits liquidation price, position is automatically closed

3. **Start Small**: Always test with small amounts first

4. **Use Stop-Loss**: Consider setting stop-loss orders manually on Binance

### Futures vs Spot Comparison

| Feature | Spot | Futures |
|---------|------|---------|
| Ownership | You own the asset | Contract only |
| Leverage | None (1x) | Up to 125x |
| Shorting | No | Yes |
| Risk | Price can go to $0 | Can be liquidated |
| Best For | Long-term holding | Trading, hedging |

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
