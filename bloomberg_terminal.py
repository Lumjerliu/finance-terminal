#!/usr/bin/env python3
"""
╔══════════════════════════════════════════════════════════════════════════════╗
║                     BLOOMBERG-STYLE FINANCIAL TERMINAL                        ║
║                          Pure Curses Implementation                           ║
║                    Black Background | Instant Keyboard                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
"""

import curses
import time
import random
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import threading
import aiohttp
import asyncio
import json
import urllib.request
import urllib.error
import sqlite3
import csv
import hashlib
import hmac
import base64

# ═══════════════════════════════════════════════════════════════════════════════
# API CONFIGURATION - Easy to swap APIs
# ═══════════════════════════════════════════════════════════════════════════════
#
# To use a premium API:
# 1. Get an API key from the provider
# 2. Set it as an environment variable: export MY_API_KEY="your_key"
# 3. Or paste it directly below
#
# Premium alternatives:
#   - Crypto: CoinGecko Pro ($129/mo), Coinbase Pro API
#   - Metals: Metals-API ($15/mo), GoldAPI.io
#   - Forex: Fixer ($10/mo), Open Exchange Rates
#   - Oil: OilPriceAPI ($29/mo), EIA API
#   - Stocks: Alpha Vantage ($50/mo), IEX Cloud ($9/mo), Polygon.io
#
# ═══════════════════════════════════════════════════════════════════════════════

API_ENDPOINTS = {
    # Crypto - Binance (Free, no key required)
    'crypto': {
        'provider': 'binance',
        'base_url': 'https://api.binance.com/api/v3',
        'api_key': '',  # Not required for public endpoints
        'symbols': {
            'BTCUSDT': 'BTC',
            'ETHUSDT': 'ETH',
            'SOLUSDT': 'SOL',
            'XRPUSDT': 'XRP',
            'DOGEUSDT': 'DOGE',
            'ADAUSDT': 'ADA',
            'AVAXUSDT': 'AVAX',
            'LINKUSDT': 'LINK',
        }
    },
    
    # Metals - Gold-API.com (Free, no key required)
    'metals': {
        'provider': 'gold-api',
        'base_url': 'https://api.gold-api.com/price',
        'api_key': '',  # Not required
        'symbols': {
            'XAU': ('GOLD', 'Gold'),
            'XAG': ('SILVER', 'Silver'),
            'HG': ('COPPER', 'Copper'),
        }
    },
    
    # Forex - Frankfurter (Free, no key required)
    'forex': {
        'provider': 'frankfurter',
        'base_url': 'https://api.frankfurter.app',
        'api_key': '',  # Not required
    },
    
    # Oil - FRED (Free, no key required)
    'oil': {
        'provider': 'fred',
        'base_url': 'https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO',
        'api_key': '',  # Not required
    },
    
    # Stocks - Yahoo Finance (Free but rate-limited)
    'stocks': {
        'provider': 'yahoo',
        'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart',
        'api_key': '',  # Not required but may be rate-limited
        'symbols': ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT', 'DIS', 'NFLX']
    },
    
    # Indices - Yahoo Finance
    'indices': {
        'provider': 'yahoo',
        'base_url': 'https://query1.finance.yahoo.com/v8/finance/chart',
        'api_key': '',
        'symbols': {
            '^GSPC': ('SPX', 'S&P 500'),
            '^DJI': ('DJI', 'Dow Jones'),
            '^IXIC': ('NDQ', 'NASDAQ'),
            '^VIX': ('VIX', 'Volatility'),
            '^RUT': ('RUT', 'Russell 2000'),
        }
    },
}

# ═══════════════════════════════════════════════════════════════════════════════
# BINANCE TRADING CONFIGURATION
# ═══════════════════════════════════════════════════════════════════════════════
#
# To enable trading, you need Binance API keys with trading permissions.
#
# SECURITY WARNING: 
# - NEVER commit API keys to git
# - Use environment variables or a separate config file
# - Use API keys with IP whitelist restriction
# - For futures, enable futures permission in Binance API settings
#
# Setup:
# 1. Create API key at https://www.binance.com/en/my/settings/api-management
# 2. Enable "Enable Spot & Margin Trading" for spot trading
# 3. Enable "Enable Futures" for futures trading
# 4. Set IP whitelist for security
# 5. Export keys as environment variables:
#    export BINANCE_API_KEY="your_api_key"
#    export BINANCE_API_SECRET="your_secret_key"
#
# Or create a file 'trading_config.py' with:
#    BINANCE_API_KEY = "your_api_key"
#    BINANCE_API_SECRET = "your_secret_key"
#
# ═══════════════════════════════════════════════════════════════════════════════

# Load API keys from environment or config file
BINANCE_API_KEY = os.environ.get('BINANCE_API_KEY', '')
BINANCE_API_SECRET = os.environ.get('BINANCE_API_SECRET', '')

# Try to load from config file if env vars not set
if not BINANCE_API_KEY:
    try:
        from trading_config import BINANCE_API_KEY as _key, BINANCE_API_SECRET as _secret
        BINANCE_API_KEY = _key
        BINANCE_API_SECRET = _secret
    except ImportError:
        pass

# Trading settings
TRADING_ENABLED = bool(BINANCE_API_KEY and BINANCE_API_SECRET)
BINANCE_SPOT_URL = "https://api.binance.com"
BINANCE_FUTURES_URL = "https://fapi.binance.com"


# ═══════════════════════════════════════════════════════════════════════════════
# BINANCE TRADING FUNCTIONS
# ═══════════════════════════════════════════════════════════════════════════════

def binance_signature(query_string: str) -> str:
    """Generate HMAC SHA256 signature for Binance API"""
    return hmac.new(
        BINANCE_API_SECRET.encode('utf-8'),
        query_string.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()


def binance_request(method: str, endpoint: str, params: dict = None, futures: bool = False) -> Optional[dict]:
    """Make authenticated request to Binance API
    
    Args:
        method: HTTP method ('GET', 'POST', 'DELETE')
        endpoint: API endpoint (e.g., '/api/v3/order')
        params: Request parameters
        futures: Use futures API instead of spot
    """
    if not TRADING_ENABLED:
        return None
    
    base_url = BINANCE_FUTURES_URL if futures else BINANCE_SPOT_URL
    
    # Add timestamp
    if params is None:
        params = {}
    params['timestamp'] = int(time.time() * 1000)
    
    # Build query string
    query_string = '&'.join([f"{k}={v}" for k, v in sorted(params.items())])
    
    # Add signature
    signature = binance_signature(query_string)
    query_string += f"&signature={signature}"
    
    # Build URL
    url = f"{base_url}{endpoint}?{query_string}"
    
    headers = {
        'X-MBX-APIKEY': BINANCE_API_KEY,
        'Content-Type': 'application/json'
    }
    
    try:
        req = urllib.request.Request(url, headers=headers, method=method)
        with urllib.request.urlopen(req, timeout=10) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ''
        return {'error': True, 'code': e.code, 'message': error_body}
    except Exception as e:
        return {'error': True, 'message': str(e)}


def get_spot_balance() -> Optional[List[dict]]:
    """Get spot account balance"""
    result = binance_request('GET', '/api/v3/account')
    
    if result and 'balances' in result:
        # Filter non-zero balances
        balances = []
        for b in result['balances']:
            free = float(b['free'])
            locked = float(b['locked'])
            if free > 0 or locked > 0:
                balances.append({
                    'asset': b['asset'],
                    'free': free,
                    'locked': locked,
                    'total': free + locked
                })
        return sorted(balances, key=lambda x: x['total'], reverse=True)
    return None


def get_futures_balance() -> Optional[List[dict]]:
    """Get futures account balance"""
    result = binance_request('GET', '/fapi/v2/balance', futures=True)
    
    if result and isinstance(result, list):
        # Filter non-zero balances
        balances = []
        for b in result:
            balance = float(b['balance'])
            if balance > 0:
                balances.append({
                    'asset': b['asset'],
                    'balance': balance,
                    'available': float(b['availableBalance']),
                    'cross_wallet': float(b['crossWalletBalance']),
                    'cross_un pnl': float(b['crossUnPnl'])
                })
        return balances
    return None


def get_futures_positions() -> Optional[List[dict]]:
    """Get open futures positions"""
    result = binance_request('GET', '/fapi/v2/positionRisk', futures=True)
    
    if result and isinstance(result, list):
        positions = []
        for p in result:
            position_amt = float(p['positionAmt'])
            if position_amt != 0:
                positions.append({
                    'symbol': p['symbol'],
                    'position_amt': position_amt,
                    'entry_price': float(p['entryPrice']),
                    'mark_price': float(p['markPrice']),
                    'unrealized_pnl': float(p['unRealizedProfit']),
                    'liquidation_price': float(p['liquidationPrice']),
                    'leverage': int(p['leverage']),
                    'margin_type': p['marginType'],
                    'side': 'LONG' if position_amt > 0 else 'SHORT'
                })
        return positions
    return None


def set_leverage(symbol: str, leverage: int) -> Optional[dict]:
    """Set leverage for futures trading
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        leverage: Leverage multiplier (1-125)
    """
    return binance_request('POST', '/fapi/v1/leverage', 
                          {'symbol': symbol.upper(), 'leverage': leverage}, 
                          futures=True)


def spot_market_buy(symbol: str, quantity: float) -> Optional[dict]:
    """Execute spot market buy order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to buy
    """
    params = {
        'symbol': symbol.upper(),
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': quantity
    }
    return binance_request('POST', '/api/v3/order', params)


def spot_market_sell(symbol: str, quantity: float) -> Optional[dict]:
    """Execute spot market sell order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to sell
    """
    params = {
        'symbol': symbol.upper(),
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': quantity
    }
    return binance_request('POST', '/api/v3/order', params)


def spot_limit_buy(symbol: str, quantity: float, price: float) -> Optional[dict]:
    """Execute spot limit buy order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to buy
        price: Limit price
    """
    params = {
        'symbol': symbol.upper(),
        'side': 'BUY',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': price
    }
    return binance_request('POST', '/api/v3/order', params)


def spot_limit_sell(symbol: str, quantity: float, price: float) -> Optional[dict]:
    """Execute spot limit sell order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to sell
        price: Limit price
    """
    params = {
        'symbol': symbol.upper(),
        'side': 'SELL',
        'type': 'LIMIT',
        'timeInForce': 'GTC',
        'quantity': quantity,
        'price': price
    }
    return binance_request('POST', '/api/v3/order', params)


def futures_market_long(symbol: str, quantity: float, leverage: int = 1) -> Optional[dict]:
    """Open futures long position with market order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to buy
        leverage: Leverage multiplier
    """
    # Set leverage first
    set_leverage(symbol, leverage)
    
    params = {
        'symbol': symbol.upper(),
        'side': 'BUY',
        'type': 'MARKET',
        'quantity': quantity
    }
    return binance_request('POST', '/fapi/v1/order', params, futures=True)


def futures_market_short(symbol: str, quantity: float, leverage: int = 1) -> Optional[dict]:
    """Open futures short position with market order
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
        quantity: Quantity to sell
        leverage: Leverage multiplier
    """
    # Set leverage first
    set_leverage(symbol, leverage)
    
    params = {
        'symbol': symbol.upper(),
        'side': 'SELL',
        'type': 'MARKET',
        'quantity': quantity
    }
    return binance_request('POST', '/fapi/v1/order', params, futures=True)


def futures_close_position(symbol: str) -> Optional[dict]:
    """Close all positions for a symbol (market order)
    
    Args:
        symbol: Trading pair (e.g., 'BTCUSDT')
    """
    # Get current position
    positions = get_futures_positions()
    if not positions:
        return {'error': True, 'message': 'No open positions'}
    
    position = None
    for p in positions:
        if p['symbol'] == symbol.upper():
            position = p
            break
    
    if not position:
        return {'error': True, 'message': f'No position for {symbol}'}
    
    # Close with opposite order
    quantity = abs(position['position_amt'])
    side = 'SELL' if position['side'] == 'LONG' else 'BUY'
    
    params = {
        'symbol': symbol.upper(),
        'side': side,
        'type': 'MARKET',
        'quantity': quantity
    }
    return binance_request('POST', '/fapi/v1/order', params, futures=True)


def get_open_orders(symbol: str = None, futures: bool = False) -> Optional[List[dict]]:
    """Get open orders
    
    Args:
        symbol: Trading pair (optional, returns all if not specified)
        futures: Check futures orders instead of spot
    """
    params = {}
    if symbol:
        params['symbol'] = symbol.upper()
    
    endpoint = '/fapi/v1/openOrders' if futures else '/api/v3/openOrders'
    result = binance_request('GET', endpoint, params, futures=futures)
    
    if result and isinstance(result, list):
        orders = []
        for o in result:
            orders.append({
                'order_id': o['orderId'],
                'symbol': o['symbol'],
                'side': o['side'],
                'type': o['type'],
                'price': float(o['price']),
                'quantity': float(o['origQty']),
                'filled': float(o['executedQty']),
                'status': o['status'],
                'time': datetime.fromtimestamp(o['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S')
            })
        return orders
    return None


def cancel_order(symbol: str, order_id: int, futures: bool = False) -> Optional[dict]:
    """Cancel an open order
    
    Args:
        symbol: Trading pair
        order_id: Order ID to cancel
        futures: Cancel futures order
    """
    params = {
        'symbol': symbol.upper(),
        'orderId': order_id
    }
    endpoint = '/fapi/v1/order' if futures else '/api/v3/order'
    return binance_request('DELETE', endpoint, params, futures=futures)


def cancel_all_orders(symbol: str, futures: bool = False) -> Optional[dict]:
    """Cancel all open orders for a symbol
    
    Args:
        symbol: Trading pair
        futures: Cancel futures orders
    """
    params = {'symbol': symbol.upper()}
    endpoint = '/fapi/v1/allOpenOrders' if futures else '/api/v3/openOrders'
    return binance_request('DELETE', endpoint, params, futures=futures)


def get_trade_history_api(symbol: str = None, limit: int = 20, futures: bool = False) -> Optional[List[dict]]:
    """Get recent trade history from exchange
    
    Args:
        symbol: Trading pair (optional)
        limit: Number of trades to return
        futures: Get futures trades
    """
    params = {'limit': limit}
    if symbol:
        params['symbol'] = symbol.upper()
    
    endpoint = '/fapi/v1/userTrades' if futures else '/api/v3/myTrades'
    result = binance_request('GET', endpoint, params, futures=futures)
    
    if result and isinstance(result, list):
        trades = []
        for t in result:
            trades.append({
                'trade_id': t['id'],
                'order_id': t['orderId'],
                'symbol': t['symbol'],
                'side': 'BUY' if t['isBuyer'] else 'SELL',
                'price': float(t['price']),
                'quantity': float(t['qty']),
                'commission': float(t['commission']),
                'commission_asset': t['commissionAsset'],
                'time': datetime.fromtimestamp(t['time'] / 1000).strftime('%Y-%m-%d %H:%M:%S'),
                'realized_pnl': float(t.get('realizedProfit', 0)) if futures else 0
            })
        return trades
    return None

# ═══════════════════════════════════════════════════════════════════════════════
# TRADE HISTORY DATABASE
# ═══════════════════════════════════════════════════════════════════════════════

# Database file location (same directory as the script)
TRADE_DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trades.db')
TRADE_CSV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'trade_history.csv')


def init_trade_database():
    """Initialize the trade history database"""
    conn = sqlite3.connect(TRADE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'completed',
            notes TEXT
        )
    ''')
    
    conn.commit()
    conn.close()


def record_trade(symbol: str, side: str, quantity: float, price: float, notes: str = "") -> int:
    """Record a trade to the database
    
    Args:
        symbol: Trading symbol (e.g., 'BTC', 'ETH')
        side: 'BUY' or 'SELL'
        quantity: Amount traded
        price: Price per unit
        notes: Optional notes
    
    Returns:
        Trade ID
    """
    init_trade_database()
    
    conn = sqlite3.connect(TRADE_DB_PATH)
    cursor = conn.cursor()
    
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    total = quantity * price
    
    cursor.execute('''
        INSERT INTO trades (timestamp, symbol, side, quantity, price, total, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (timestamp, symbol.upper(), side.upper(), quantity, price, total, notes))
    
    trade_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    # Also append to CSV for easy backup/viewing
    try:
        with open(TRADE_CSV_PATH, 'a', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([trade_id, timestamp, symbol.upper(), side.upper(), 
                           quantity, price, total, 'completed', notes])
    except Exception:
        pass
    
    return trade_id


def get_trade_history(limit: int = 50) -> List[Dict]:
    """Get trade history from database
    
    Args:
        limit: Maximum number of trades to return
    
    Returns:
        List of trade dictionaries
    """
    init_trade_database()
    
    conn = sqlite3.connect(TRADE_DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM trades 
        ORDER BY timestamp DESC 
        LIMIT ?
    ''', (limit,))
    
    trades = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return trades


def get_trade_summary() -> Dict:
    """Get summary statistics of all trades"""
    init_trade_database()
    
    conn = sqlite3.connect(TRADE_DB_PATH)
    cursor = conn.cursor()
    
    # Total trades
    cursor.execute('SELECT COUNT(*) FROM trades')
    total_trades = cursor.fetchone()[0]
    
    # Total buys and sells
    cursor.execute('SELECT COUNT(*) FROM trades WHERE side = "BUY"')
    total_buys = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM trades WHERE side = "SELL"')
    total_sells = cursor.fetchone()[0]
    
    # Total volume by symbol
    cursor.execute('''
        SELECT symbol, SUM(total) as total_volume 
        FROM trades 
        GROUP BY symbol 
        ORDER BY total_volume DESC
    ''')
    volume_by_symbol = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    
    return {
        'total_trades': total_trades,
        'total_buys': total_buys,
        'total_sells': total_sells,
        'volume_by_symbol': volume_by_symbol
    }


def delete_trade(trade_id: int) -> bool:
    """Delete a trade by ID"""
    init_trade_database()
    
    conn = sqlite3.connect(TRADE_DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM trades WHERE id = ?', (trade_id,))
    deleted = cursor.rowcount > 0
    
    conn.commit()
    conn.close()
    
    return deleted


# ═══════════════════════════════════════════════════════════════════════════════
# COLOR PALETTE - Bloomberg Style
# ═══════════════════════════════════════════════════════════════════════════════

# Color pair numbers (curses requires color pairs)
COLOR_BLACK = 0
COLOR_AMBER = 1      # Bloomberg signature orange/amber
COLOR_GREEN = 2      # Gainers
COLOR_RED = 3        # Losers  
COLOR_WHITE = 4      # Normal text
COLOR_YELLOW = 5     # Highlights
COLOR_CYAN = 6       # Info
COLOR_DIM = 7        # Dimmed text


def init_colors():
    """Initialize curses color palette - Bloomberg style"""
    curses.start_color()
    curses.use_default_colors()
    
    # Define custom colors (RGB values approximated for terminal)
    # Color pair (foreground, background) - all with black background (-1 or 0)
    
    # Bloomberg amber/orange
    curses.init_pair(COLOR_AMBER, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    # Green for gains
    curses.init_pair(COLOR_GREEN, curses.COLOR_GREEN, curses.COLOR_BLACK)
    # Red for losses
    curses.init_pair(COLOR_RED, curses.COLOR_RED, curses.COLOR_BLACK)
    # White for normal text
    curses.init_pair(COLOR_WHITE, curses.COLOR_WHITE, curses.COLOR_BLACK)
    # Yellow for highlights
    curses.init_pair(COLOR_YELLOW, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    # Cyan for info
    curses.init_pair(COLOR_CYAN, curses.COLOR_CYAN, curses.COLOR_BLACK)
    # Dim gray for secondary text
    curses.init_pair(COLOR_DIM, 8, curses.COLOR_BLACK)  # Color 8 is bright black (gray)


# ═══════════════════════════════════════════════════════════════════════════════
# REAL MARKET DATA APIs
# ═══════════════════════════════════════════════════════════════════════════════

def fetch_url(url: str, timeout: int = 5) -> Optional[dict]:
    """Fetch JSON from URL with error handling"""
    try:
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        with urllib.request.urlopen(req, timeout=timeout) as response:
            return json.loads(response.read().decode())
    except Exception as e:
        return None


def get_crypto_prices() -> Dict:
    """Fetch real crypto prices from Binance API (free, no API key needed)"""
    data = {}
    # Binance symbol mappings
    symbols = {
        'BTCUSDT': 'BTC',
        'ETHUSDT': 'ETH',
        'SOLUSDT': 'SOL',
        'XRPUSDT': 'XRP',
        'DOGEUSDT': 'DOGE',
        'ADAUSDT': 'ADA',
        'AVAXUSDT': 'AVAX',
        'LINKUSDT': 'LINK'
    }
    
    for binance_sym, display_sym in symbols.items():
        try:
            url = f"https://api.binance.com/api/v3/ticker/24hr?symbol={binance_sym}"
            result = fetch_url(url)
            
            if result:
                price = float(result.get('lastPrice', 0))
                change_pct = float(result.get('priceChangePercent', 0))
                
                if price:
                    data[display_sym] = {
                        'price': price,
                        'change': price * change_pct / 100,
                        'pct': change_pct,
                        'name': display_sym
                    }
        except Exception:
            pass
    return data


def get_stock_prices() -> Dict:
    """Fetch real stock prices from Yahoo Finance (free, unofficial)"""
    data = {}
    symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'JPM', 'V', 'WMT', 'DIS', 'NFLX']
    
    for symbol in symbols:
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            result = fetch_url(url)
            
            if result and 'chart' in result and 'result' in result['chart']:
                chart_data = result['chart']['result']
                if chart_data:
                    meta = chart_data[0].get('meta', {})
                    price = meta.get('regularMarketPrice', 0)
                    prev_close = meta.get('previousClose', price)
                    
                    if price and prev_close:
                        change = price - prev_close
                        pct = (change / prev_close) * 100 if prev_close else 0
                        data[symbol] = {
                            'price': price,
                            'change': change,
                            'pct': pct,
                            'name': meta.get('shortName', symbol)[:20]
                        }
        except Exception:
            pass
        time.sleep(0.1)  # Rate limiting
    return data


def get_forex_prices() -> Dict:
    """Fetch real forex prices from Frankfurter API (free, no key)"""
    data = {}
    try:
        # Frankfurter API - free, no key, reliable
        url = "https://api.frankfurter.app/latest?from=USD&to=EUR,GBP,JPY,CHF,AUD,CAD"
        result = fetch_url(url)
        
        if result and 'rates' in result:
            rates = result['rates']
            
            # EUR/USD = 1 / EUR rate
            if 'EUR' in rates:
                eur_usd = 1 / rates['EUR']
                data['EUR/USD'] = {
                    'price': eur_usd,
                    'change': 0,  # Frankfurter doesn't provide change
                    'pct': 0,
                    'name': 'Euro/Dollar'
                }
            
            if 'GBP' in rates:
                gbp_usd = 1 / rates['GBP']
                data['GBP/USD'] = {
                    'price': gbp_usd,
                    'change': 0,
                    'pct': 0,
                    'name': 'Pound/Dollar'
                }
            
            if 'JPY' in rates:
                data['USD/JPY'] = {
                    'price': rates['JPY'],
                    'change': 0,
                    'pct': 0,
                    'name': 'Dollar/Yen'
                }
            
            if 'CHF' in rates:
                data['USD/CHF'] = {
                    'price': rates['CHF'],
                    'change': 0,
                    'pct': 0,
                    'name': 'Dollar/Swiss'
                }
            
            if 'AUD' in rates:
                data['AUD/USD'] = {
                    'price': 1 / rates['AUD'],
                    'change': 0,
                    'pct': 0,
                    'name': 'Aussie/Dollar'
                }
            
            if 'CAD' in rates:
                data['USD/CAD'] = {
                    'price': rates['CAD'],
                    'change': 0,
                    'pct': 0,
                    'name': 'Dollar/Loonie'
                }
    except Exception:
        pass
    return data


def get_commodity_prices() -> Dict:
    """Fetch real commodity prices from Gold-API (free, no key)"""
    data = {}
    
    # Gold-API.com - free, no key required
    metals = {
        'XAU': ('GOLD', 'Gold'),
        'XAG': ('SILVER', 'Silver'),
        'HG': ('COPPER', 'Copper'),
    }
    
    for symbol, (display, name) in metals.items():
        try:
            url = f"https://api.gold-api.com/price/{symbol}"
            result = fetch_url(url)
            
            if result and 'price' in result:
                price = result['price']
                # Gold-API doesn't provide 24h change, set to 0
                data[display] = {
                    'price': price,
                    'change': 0,
                    'pct': 0,
                    'name': name
                }
        except Exception:
            pass
    
    # Oil from FRED (CSV format)
    try:
        url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DCOILWTICO"
        req = urllib.request.Request(url, headers={
            'User-Agent': 'Mozilla/5.0'
        })
        with urllib.request.urlopen(req, timeout=5) as response:
            csv_data = response.read().decode()
            lines = csv_data.strip().split('\n')
            # Find last non-empty value
            for line in reversed(lines[1:]):  # Skip header
                if ',' in line:
                    parts = line.split(',')
                    if len(parts) >= 2 and parts[1] and parts[1] != '.':
                        price = float(parts[1])
                        data['OIL'] = {
                            'price': price,
                            'change': 0,
                            'pct': 0,
                            'name': 'Crude Oil (WTI)'
                        }
                        break
    except Exception:
        pass
    
    # Natural Gas from Yahoo Finance (try)
    try:
        url = "https://query1.finance.yahoo.com/v8/finance/chart/NG=F?interval=1d&range=1d"
        result = fetch_url(url)
        if result and 'chart' in result and result['chart'].get('result'):
            meta = result['chart']['result'][0].get('meta', {})
            price = meta.get('regularMarketPrice', 0)
            if price:
                data['NATGAS'] = {
                    'price': price,
                    'change': 0,
                    'pct': 0,
                    'name': 'Natural Gas'
                }
    except Exception:
        pass
    
    return data


def get_index_prices() -> Dict:
    """Fetch real index prices from Yahoo Finance"""
    data = {}
    indices = {
        '^GSPC': ('SPX', 'S&P 500'),
        '^DJI': ('DJI', 'Dow Jones'),
        '^IXIC': ('NDQ', 'NASDAQ'),
        '^VIX': ('VIX', 'Volatility'),
        '^RUT': ('RUT', 'Russell 2000')
    }
    
    for symbol, (display, name) in indices.items():
        try:
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval=1d&range=1d"
            result = fetch_url(url)
            
            if result and 'chart' in result and 'result' in result['chart']:
                chart_data = result['chart']['result']
                if chart_data:
                    meta = chart_data[0].get('meta', {})
                    price = meta.get('regularMarketPrice', 0)
                    prev_close = meta.get('previousClose', price)
                    
                    if price and prev_close:
                        change = price - prev_close
                        pct = (change / prev_close) * 100 if prev_close else 0
                        data[display] = {
                            'price': price,
                            'change': change,
                            'pct': pct,
                            'name': name
                        }
        except Exception:
            pass
        time.sleep(0.1)
    return data


def get_all_real_data() -> Dict:
    """Fetch all real market data from APIs"""
    all_data = {}
    
    # 1. Crypto from Binance (most reliable)
    crypto = get_crypto_prices()
    if crypto:
        all_data.update(crypto)
    
    # 2. Forex from Frankfurter (free, no key)
    forex = get_forex_prices()
    if forex:
        all_data.update(forex)
    
    # 3. Commodities from Gold-API + FRED (free, no key)
    commodities = get_commodity_prices()
    if commodities:
        all_data.update(commodities)
    
    # 4. Indices from Yahoo Finance (may be rate limited)
    try:
        indices = get_index_prices()
        if indices:
            all_data.update(indices)
    except:
        pass
    
    # 5. Stocks from Yahoo Finance (may be rate limited)
    try:
        stocks = get_stock_prices()
        if stocks:
            all_data.update(stocks)
    except:
        pass
    
    return all_data


def get_quick_prices() -> Dict:
    """Quick fetch of most important prices using reliable free APIs"""
    data = {}
    
    # 1. Crypto from Binance (fast, reliable)
    crypto = get_crypto_prices()
    if crypto:
        data.update(crypto)
    
    # 2. Forex from Frankfurter (free, no key)
    forex = get_forex_prices()
    if forex:
        data.update(forex)
    
    # 3. Commodities from Gold-API (free, no key)
    commodities = get_commodity_prices()
    if commodities:
        data.update(commodities)
    
    return data


def get_mock_data() -> Dict:
    """Empty placeholder - no mock data"""
    return {}


# ═══════════════════════════════════════════════════════════════════════════════
# HISTORICAL PRICE DATA - Charts and Comparisons
# ═══════════════════════════════════════════════════════════════════════════════

# CoinGecko ID mappings for historical data
COINGECKO_IDS = {
    'BTC': 'bitcoin',
    'ETH': 'ethereum',
    'SOL': 'solana',
    'XRP': 'ripple',
    'DOGE': 'dogecoin',
    'ADA': 'cardano',
    'AVAX': 'avalanche-2',
    'LINK': 'chainlink',
    'DOT': 'polkadot',
    'MATIC': 'matic-network',
    'LTC': 'litecoin',
    'UNI': 'uniswap',
}

# Cache for historical data to avoid repeated API calls
_historical_cache: Dict[str, Tuple[List, float]] = {}


def get_historical_prices(symbol: str, days: int = 30) -> Optional[List[Dict]]:
    """Fetch historical price data from CoinGecko (free, no key)
    
    Args:
        symbol: Crypto symbol (BTC, ETH, etc.)
        days: Number of days of history (max 365 for free API)
    
    Returns:
        List of {'timestamp': int, 'price': float, 'date': str}
    """
    # Check cache first (cache for 5 minutes)
    cache_key = f"{symbol}_{days}"
    if cache_key in _historical_cache:
        cached_data, cache_time = _historical_cache[cache_key]
        if time.time() - cache_time < 300:  # 5 minute cache
            return cached_data
    
    coingecko_id = COINGECKO_IDS.get(symbol.upper())
    if not coingecko_id:
        return None
    
    try:
        url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart"
        params = f"?vs_currency=usd&days={days}&interval=daily"
        
        req = urllib.request.Request(url + params, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if 'prices' in result:
            data = []
            for ts, price in result['prices']:
                dt = datetime.fromtimestamp(ts / 1000)
                data.append({
                    'timestamp': ts,
                    'price': price,
                    'date': dt.strftime('%Y-%m-%d'),
                    'datetime': dt
                })
            
            # Cache the result
            _historical_cache[cache_key] = (data, time.time())
            return data
    except Exception as e:
        pass
    
    return None


def get_historical_range(symbol: str, start_date: str, end_date: str) -> Optional[List[Dict]]:
    """Fetch historical prices for a specific date range
    
    Args:
        symbol: Crypto symbol
        start_date: Start date 'YYYY-MM-DD'
        end_date: End date 'YYYY-MM-DD'
    
    Returns:
        List of price data points
    """
    coingecko_id = COINGECKO_IDS.get(symbol.upper())
    if not coingecko_id:
        return None
    
    try:
        # Convert dates to timestamps
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        
        start_ts = int(start_dt.timestamp())
        end_ts = int(end_dt.timestamp())
        
        url = f"https://api.coingecko.com/api/v3/coins/{coingecko_id}/market_chart/range"
        params = f"?vs_currency=usd&from={start_ts}&to={end_ts}"
        
        req = urllib.request.Request(url + params, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=15) as response:
            result = json.loads(response.read().decode())
        
        if 'prices' in result:
            data = []
            for ts, price in result['prices']:
                dt = datetime.fromtimestamp(ts / 1000)
                data.append({
                    'timestamp': ts,
                    'price': price,
                    'date': dt.strftime('%Y-%m-%d'),
                    'datetime': dt
                })
            return data
    except Exception:
        pass
    
    return None


class PriceChart:
    """ASCII Chart renderer for price data"""
    
    def __init__(self, width: int = 80, height: int = 20):
        self.width = width
        self.height = height
    
    def normalize_data(self, data: List[float]) -> List[float]:
        """Normalize data to 0-1 range"""
        if not data:
            return []
        min_val = min(data)
        max_val = max(data)
        if max_val == min_val:
            return [0.5] * len(data)
        return [(x - min_val) / (max_val - min_val) for x in data]
    
    def render_ascii(self, data: List[Dict], title: str = "Price Chart") -> List[str]:
        """Render ASCII chart from price data
        
        Returns list of strings (lines)
        """
        if not data:
            return ["NO DATA AVAILABLE"]
        
        prices = [d['price'] for d in data]
        dates = [d['date'] for d in data]
        
        # Normalize prices
        normalized = self.normalize_data(prices)
        
        min_price = min(prices)
        max_price = max(prices)
        
        # Chart dimensions
        chart_width = self.width - 15  # Leave room for Y-axis labels
        chart_height = self.height - 4  # Leave room for title and X-axis
        
        lines = []
        
        # Title
        lines.append(f" {title}")
        lines.append(f" Range: ${min_price:,.2f} - ${max_price:,.2f}")
        lines.append(" " + "─" * (chart_width + 10))
        
        # Create chart grid
        # Sample data points to fit chart width
        if len(normalized) > chart_width:
            step = len(normalized) / chart_width
            sampled_indices = [int(i * step) for i in range(chart_width)]
            sampled_normalized = [normalized[i] for i in sampled_indices]
            sampled_dates = [dates[i] for i in sampled_indices]
        else:
            sampled_normalized = normalized
            sampled_dates = dates
        
        # Render each row (top to bottom)
        for row in range(chart_height, 0, -1):
            threshold = row / chart_height
            line = ""
            
            for val in sampled_normalized:
                if val >= threshold:
                    line += "█"
                elif val >= threshold - 0.1:
                    line += "▄"
                else:
                    line += " "
            
            # Y-axis label
            y_val = min_price + (max_price - min_price) * (row / chart_height)
            lines.append(f" ${y_val:>10,.0f} │{line}")
        
        # X-axis
        lines.append(" " + " " * 11 + "└" + "─" * len(sampled_normalized))
        
        # X-axis labels (show first, middle, last dates)
        if len(sampled_dates) >= 3:
            first = sampled_dates[0]
            middle = sampled_dates[len(sampled_dates) // 2]
            last = sampled_dates[-1]
            label_line = " " * 12 + first
            label_line += " " * (len(sampled_normalized) // 2 - len(first) - len(middle) // 2)
            label_line += middle
            label_line += " " * (len(sampled_normalized) - len(label_line) + 12)
            label_line += last
            lines.append(label_line[:self.width])
        
        return lines
    
    def render_comparison(self, datasets: List[Tuple[str, List[Dict]]], title: str = "Comparison") -> List[str]:
        """Render multiple datasets on same chart for comparison
        
        Args:
            datasets: List of (label, price_data) tuples
        """
        if not datasets:
            return ["NO DATA AVAILABLE"]
        
        # Get all prices from all datasets
        all_prices = []
        for label, data in datasets:
            all_prices.extend([d['price'] for d in data])
        
        if not all_prices:
            return ["NO DATA AVAILABLE"]
        
        min_price = min(all_prices)
        max_price = max(all_prices)
        
        # Normalize all datasets to same scale
        normalized_datasets = []
        for label, data in datasets:
            prices = [d['price'] for d in data]
            normalized = [(p - min_price) / (max_price - min_price) if max_price > min_price else 0.5 
                         for p in prices]
            normalized_datasets.append((label, normalized, data))
        
        chart_width = self.width - 15
        chart_height = self.height - 6
        
        lines = []
        
        # Title
        lines.append(f" {title}")
        lines.append(f" Range: ${min_price:,.2f} - ${max_price:,.2f}")
        
        # Legend
        legend = "  ".join([f"● {label}" for label, _, _ in normalized_datasets])
        lines.append(f" {legend}"[:self.width])
        lines.append(" " + "─" * (chart_width + 10))
        
        # Chart characters for different datasets
        chars = ['█', '░', '▓', '▒', '■', '□']
        
        # Sample all datasets to same length
        min_len = min(len(n) for _, n, _ in normalized_datasets)
        if min_len > chart_width:
            step = min_len / chart_width
            sampled_datasets = []
            for label, normalized, data in normalized_datasets:
                sampled = [normalized[int(i * step)] for i in range(chart_width)]
                sampled_datasets.append((label, sampled))
        else:
            sampled_datasets = [(label, n[:min_len]) for label, n, _ in normalized_datasets]
        
        # Render chart
        for row in range(chart_height, 0, -1):
            threshold = row / chart_height
            line = ""
            
            for col in range(len(sampled_datasets[0][1])):
                # Find which dataset has the highest value at this column
                vals = [sampled_datasets[i][1][col] for i in range(len(sampled_datasets))]
                
                # Check if any value is at or above threshold
                char = " "
                for i, val in enumerate(vals):
                    if val >= threshold:
                        char = chars[i % len(chars)]
                        break
                    elif val >= threshold - 0.05:
                        char = chars[i % len(chars)].lower() if chars[i % len(chars)].isupper() else chars[i % len(chars)]
                        break
                
                line += char
            
            y_val = min_price + (max_price - min_price) * (row / chart_height)
            lines.append(f" ${y_val:>10,.0f} │{line}")
        
        # X-axis
        lines.append(" " + " " * 11 + "└" + "─" * len(sampled_datasets[0][1]))
        
        # Date labels from first dataset
        _, first_data = datasets[0]
        if first_data:
            dates = [d['date'] for d in first_data]
            if len(dates) >= 3:
                first = dates[0]
                middle = dates[len(dates) // 2]
                last = dates[-1]
                label_line = " " * 12 + first + " " * 10 + middle + " " * 10 + last
                lines.append(label_line[:self.width])
        
        return lines
    
    def render_percentage_change(self, datasets: List[Tuple[str, List[Dict]]], title: str = "Percentage Change") -> List[str]:
        """Render percentage change comparison (all start at 100%)"""
        if not datasets:
            return ["NO DATA AVAILABLE"]
        
        # Calculate percentage changes
        pct_datasets = []
        for label, data in datasets:
            if not data:
                continue
            start_price = data[0]['price']
            pct_changes = [(d['price'] / start_price - 1) * 100 for d in data]
            pct_datasets.append((label, pct_changes, data))
        
        if not pct_datasets:
            return ["NO DATA AVAILABLE"]
        
        # Find min/max percentage changes
        all_changes = []
        for _, changes, _ in pct_datasets:
            all_changes.extend(changes)
        
        min_pct = min(all_changes)
        max_pct = max(all_changes)
        
        # Center around 0
        max_abs = max(abs(min_pct), abs(max_pct))
        min_pct = -max_abs
        max_pct = max_abs
        
        chart_width = self.width - 15
        chart_height = self.height - 6
        
        lines = []
        
        # Title
        lines.append(f" {title}")
        lines.append(f" Range: {min_pct:+.1f}% to {max_pct:+.1f}%")
        
        # Legend
        legend = "  ".join([f"● {label}" for label, _, _ in pct_datasets])
        lines.append(f" {legend}"[:self.width])
        lines.append(" " + "─" * (chart_width + 10))
        
        # Chart characters
        chars = ['█', '░', '▓']
        
        # Sample to fit width
        min_len = min(len(c) for _, c, _ in pct_datasets)
        if min_len > chart_width:
            step = min_len / chart_width
            sampled = [(label, [changes[int(i * step)] for i in range(chart_width)]) 
                      for label, changes, _ in pct_datasets]
        else:
            sampled = [(label, c[:min_len]) for label, c, _ in pct_datasets]
        
        # Render chart
        for row in range(chart_height, 0, -1):
            threshold = min_pct + (max_pct - min_pct) * (row / chart_height)
            line = ""
            
            for col in range(len(sampled[0][1])):
                vals = [s[1][col] for s in sampled]
                
                char = " "
                for i, val in enumerate(vals):
                    if val >= threshold:
                        char = chars[i % len(chars)]
                        break
                    elif val >= threshold - (max_pct - min_pct) / chart_height * 2:
                        char = chars[i % len(chars)]
                        break
                
                line += char
            
            # Y-axis label with % sign
            y_val = min_pct + (max_pct - min_pct) * (row / chart_height)
            lines.append(f" {y_val:>+10.1f}% │{line}")
        
        # X-axis
        lines.append(" " + " " * 11 + "└" + "─" * len(sampled[0][1]))
        
        # Zero line indicator
        zero_row = int((0 - min_pct) / (max_pct - min_pct) * chart_height)
        lines.append(f" (0% baseline at row {chart_height - zero_row})")
        
        return lines


# Featured assets to highlight at the top
FEATURED_ASSETS = ["BTC", "ETH", "SPX", "GOLD", "OIL", "EUR/USD"]


# ═══════════════════════════════════════════════════════════════════════════════
# NEWS HEADLINES - RSS and Reddit Sources
# ═══════════════════════════════════════════════════════════════════════════════

# News sources - RSS feeds (free, converted via rss2json.com)
NEWS_SOURCES = {
    'business': {
        'name': 'Business News',
        'sources': [
            ('Reddit Business', 'https://www.reddit.com/r/business/hot.json?limit=15'),
        ]
    },
    'stocks': {
        'name': 'Stock Market',
        'sources': [
            ('Reddit Stocks', 'https://www.reddit.com/r/stocks/hot.json?limit=15'),
        ]
    },
    'crypto': {
        'name': 'Crypto News',
        'sources': [
            ('Reddit Crypto', 'https://www.reddit.com/r/CryptoCurrency/hot.json?limit=15'),
        ]
    },
    'politics': {
        'name': 'Politics',
        'sources': [
            ('Reddit Politics', 'https://www.reddit.com/r/politics/hot.json?limit=15'),
        ]
    },
    'world': {
        'name': 'World News',
        'sources': [
            ('Reddit WorldNews', 'https://www.reddit.com/r/worldnews/hot.json?limit=15'),
        ]
    },
}

# Reddit sources for discussions (free JSON API, no key)
REDDIT_SOURCES = {
    'stocks': 'https://www.reddit.com/r/stocks/hot.json?limit=15',
    'wallstreetbets': 'https://www.reddit.com/r/wallstreetbets/hot.json?limit=15',
    'crypto': 'https://www.reddit.com/r/CryptoCurrency/hot.json?limit=15',
    'politics': 'https://www.reddit.com/r/politics/hot.json?limit=15',
    'economy': 'https://www.reddit.com/r/economy/hot.json?limit=15',
    'business': 'https://www.reddit.com/r/business/hot.json?limit=15',
    'worldnews': 'https://www.reddit.com/r/worldnews/hot.json?limit=15',
    'investing': 'https://www.reddit.com/r/investing/hot.json?limit=15',
    'options': 'https://www.reddit.com/r/options/hot.json?limit=15',
    'forex': 'https://www.reddit.com/r/Forex/hot.json?limit=15',
}

# News cache
_news_cache: Dict[str, Tuple[List, float]] = {}
NEWS_CACHE_DURATION = 300  # 5 minutes


def fetch_rss_news(rss_url: str, limit: int = 10) -> List[Dict]:
    """Fetch news from RSS feed via rss2json converter (free, no key)
    
    Args:
        rss_url: RSS feed URL
        limit: Maximum number of articles
    
    Returns:
        List of news articles
    """
    try:
        # Use rss2json.com to convert RSS to JSON (free, no key)
        converter_url = f"https://api.rss2json.com/v1/api.json?rss_url={urllib.parse.quote(rss_url)}&count={limit}"
        
        req = urllib.request.Request(converter_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if result.get('status') == 'ok' and 'items' in result:
            articles = []
            for item in result['items'][:limit]:
                articles.append({
                    'title': item.get('title', 'No title'),
                    'link': item.get('link', ''),
                    'pubDate': item.get('pubDate', ''),
                    'source': item.get('author', 'Unknown'),
                    'description': item.get('description', '')[:200] + '...' if len(item.get('description', '')) > 200 else item.get('description', ''),
                })
            return articles
    except Exception:
        pass
    
    return []


def fetch_reddit_posts(subreddit_url: str, limit: int = 10) -> List[Dict]:
    """Fetch posts from Reddit (free JSON API, no key)
    
    Args:
        subreddit_url: Reddit subreddit JSON URL
        limit: Maximum number of posts
    
    Returns:
        List of posts
    """
    try:
        req = urllib.request.Request(subreddit_url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        with urllib.request.urlopen(req, timeout=10) as response:
            result = json.loads(response.read().decode())
        
        if 'data' in result and 'children' in result['data']:
            posts = []
            for child in result['data']['children'][:limit]:
                post_data = child.get('data', {})
                posts.append({
                    'title': post_data.get('title', 'No title'),
                    'link': f"https://reddit.com{post_data.get('permalink', '')}",
                    'score': post_data.get('score', 0),
                    'comments': post_data.get('num_comments', 0),
                    'subreddit': post_data.get('subreddit', ''),
                    'author': post_data.get('author', 'Unknown'),
                })
            return posts
    except Exception:
        pass
    
    return []


def get_news(category: str = 'business', use_cache: bool = True) -> List[Dict]:
    """Get news headlines for a category (from Reddit)
    
    Args:
        category: News category (business, stocks, crypto, politics, world)
        use_cache: Whether to use cached data
    
    Returns:
        List of news articles
    """
    cache_key = f"news_{category}"
    
    # Check cache
    if use_cache and cache_key in _news_cache:
        cached_data, cache_time = _news_cache[cache_key]
        if time.time() - cache_time < NEWS_CACHE_DURATION:
            return cached_data
    
    # Map category to subreddit
    category_map = {
        'business': 'business',
        'stocks': 'stocks',
        'crypto': 'CryptoCurrency',
        'politics': 'politics',
        'world': 'worldnews',
    }
    
    subreddit = category_map.get(category, category)
    url = f"https://www.reddit.com/r/{subreddit}/hot.json?limit=15"
    
    articles = fetch_reddit_posts(url, limit=15)
    
    # Cache results
    if articles:
        _news_cache[cache_key] = (articles, time.time())
    
    return articles


def get_reddit_news(category: str = 'stocks', use_cache: bool = True) -> List[Dict]:
    """Get Reddit posts for a category
    
    Args:
        category: Reddit category (stocks, wallstreetbets, crypto, politics, economy)
        use_cache: Whether to use cached data
    
    Returns:
        List of Reddit posts
    """
    cache_key = f"reddit_{category}"
    
    # Check cache
    if use_cache and cache_key in _news_cache:
        cached_data, cache_time = _news_cache[cache_key]
        if time.time() - cache_time < NEWS_CACHE_DURATION:
            return cached_data
    
    posts = []
    
    # Fetch from Reddit
    if category in REDDIT_SOURCES:
        posts = fetch_reddit_posts(REDDIT_SOURCES[category], limit=15)
    
    # Cache results
    if posts:
        _news_cache[cache_key] = (posts, time.time())
    
    return posts


def get_all_news() -> Dict[str, List[Dict]]:
    """Get news from all categories"""
    return {
        'business': get_news('business'),
        'stocks': get_news('stocks'),
        'crypto': get_news('crypto'),
        'politics': get_news('politics'),
    }


import urllib.parse


def update_prices(data: Dict) -> Dict:
    """Simulate real-time price updates"""
    for sym in data:
        change_pct = random.uniform(-0.05, 0.05)
        data[sym]["price"] *= (1 + change_pct / 100)
        data[sym]["change"] = data[sym]["price"] * data[sym]["pct"] / 100
    return data


# ═══════════════════════════════════════════════════════════════════════════════
# BLOOMBERG TERMINAL CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class BloombergTerminal:
    
    def __init__(self, stdscr):
        self.screen = stdscr
        self.data = {}  # Start with no data
        self.command = ""
        self.running = True
        self.messages: List[Tuple[str, str]] = []
        self.focused = None
        self.height = 0
        self.width = 0
        self.last_update = time.time()
        self.data_refresh_counter = 0
        self.api_status = "CONNECTING..."  # Track API status
        self.last_fetch_time = None
        self.fetch_errors = []  # Track which APIs failed
        self.view_mode = "main"  # Current view: "main", "history", "asset", "chart", "news"
        
        # Chart data storage
        self.chart_data = None  # Current chart data to display
        self.chart_title = ""
        self.chart_lines = []  # Rendered chart lines
        
        # News data storage
        self.news_data = []  # Current news articles to display
        self.news_category = "business"  # Current news category
        self.news_source = "rss"  # "rss" or "reddit"
        
        # Setup curses
        self.setup()
        self.add_message("Connecting to APIs...", "info")
    
    def setup(self):
        """Initialize curses settings"""
        # Get screen dimensions
        self.height, self.width = self.screen.getmaxyx()
        
        # Initialize colors
        init_colors()
        
        # Curses settings
        self.screen.nodelay(True)   # Non-blocking input
        self.screen.clearok(True)   # Clear on refresh
        self.screen.idcok(False)    # Don't use insert/delete char
        self.screen.idlok(False)    # Don't use insert/delete line
        curses.curs_set(0)          # Hide cursor initially
        curses.noecho()             # Don't echo input
        curses.cbreak()             # Instant input
        
        # Set background to black
        self.screen.bkgd(' ', curses.color_pair(COLOR_WHITE))
        
        # Clear screen
        self.screen.clear()
        self.screen.refresh()
    
    def add_message(self, msg: str, msg_type: str = "info"):
        """Add a status message"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.messages.append((timestamp, msg, msg_type))
        if len(self.messages) > 5:
            self.messages.pop(0)
    
    def format_price(self, price: float) -> str:
        """Format price for display"""
        if price >= 10000:
            return f"{price:,.0f}"
        elif price >= 1000:
            return f"{price:,.2f}"
        elif price >= 1:
            return f"{price:,.2f}"
        else:
            return f"{price:.4f}"
    
    def draw_line(self, y: int, text: str, color: int = COLOR_WHITE, bold: bool = False):
        """Draw a line at position y with color"""
        if y >= self.height - 1:
            return
        try:
            attr = curses.color_pair(color)
            if bold:
                attr |= curses.A_BOLD
            self.screen.addstr(y, 0, text.ljust(self.width - 1), attr)
        except curses.error:
            pass
    
    def draw_text(self, y: int, x: int, text: str, color: int = COLOR_WHITE, bold: bool = False):
        """Draw text at position (y, x) with color"""
        if y >= self.height - 1 or x >= self.width - 1:
            return
        try:
            attr = curses.color_pair(color)
            if bold:
                attr |= curses.A_BOLD
            self.screen.addstr(y, x, text, attr)
        except curses.error:
            pass
    
    def draw_header(self, y: int):
        """Draw the Bloomberg-style header"""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Top border
        self.draw_line(y, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        
        # Title line
        title = "  BLOOMBERG  TERMINAL  "
        padding = (self.width - len(title) - 30) // 2
        if padding < 0:
            padding = 0
        header_line = f"║{title}{' ' * padding}REAL-TIME MARKET DATA{' ' * (self.width - 50 - padding)}║"
        self.draw_line(y + 1, header_line[:self.width-1], COLOR_AMBER, bold=True)
        
        # Status line with API status
        status_color = COLOR_GREEN if "LIVE" in self.api_status else (COLOR_RED if "ERROR" in self.api_status else COLOR_YELLOW)
        status = f"║ {now} │ API: {self.api_status} │ Assets: {len(self.data)} │ Ctrl+C: Exit"
        status = status + " " * (self.width - len(status) - 2) + "║"
        self.draw_line(y + 2, status[:self.width-1], COLOR_AMBER)
        
        # Bottom border
        self.draw_line(y + 3, "═" * (self.width - 1), COLOR_AMBER, bold=True)
    
    def draw_ticker(self, y: int):
        """Draw scrolling market ticker"""
        ticker = "  │  ".join([
            f"{sym} {'▲' if d['change'] >= 0 else '▼'} {'+' if d['pct'] >= 0 else ''}{d['pct']:.2f}%"
            for sym, d in list(self.data.items())[:8]
        ])
        self.draw_line(y, ticker[:self.width-1], COLOR_DIM)
    
    def draw_spotlight(self, y: int):
        """Draw featured market prices in large, prominent boxes"""
        # Title
        self.draw_line(y, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        self.draw_text(y + 1, 2, "★ MARKET SPOTLIGHT ★", COLOR_YELLOW, bold=True)
        self.draw_line(y + 2, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        
        # Calculate box width (3 boxes per row)
        box_width = (self.width - 4) // 3
        
        # First row: BTC, ETH, SPX
        row1 = ["BTC", "ETH", "SPX"]
        for i, sym in enumerate(row1):
            x = i * (box_width + 1) + 1
            
            # Box border top
            self.draw_text(y + 4, x, "┌" + "─" * (box_width - 2) + "┐", COLOR_AMBER)
            
            if sym in self.data:
                d = self.data[sym]
                # Symbol name
                self.draw_text(y + 5, x + 2, d["name"][:box_width-4], COLOR_CYAN, bold=True)
                
                # Price (large)
                price_str = self.format_price(d["price"])
                self.draw_text(y + 6, x + 2, f"${price_str}", COLOR_WHITE, bold=True)
                
                # Change
                color = COLOR_GREEN if d["change"] >= 0 else COLOR_RED
                arrow = "▲" if d["change"] >= 0 else "▼"
                sign = "+" if d["pct"] >= 0 else ""
                change_str = f"{arrow} {sign}{d['pct']:.2f}%"
                self.draw_text(y + 7, x + 2, change_str, color, bold=True)
            else:
                # NO DATA
                self.draw_text(y + 5, x + 2, sym, COLOR_DIM, bold=True)
                self.draw_text(y + 6, x + 2, "NO DATA", COLOR_RED, bold=True)
                self.draw_text(y + 7, x + 2, "─" * 8, COLOR_DIM)
            
            # Box border bottom
            self.draw_text(y + 8, x, "└" + "─" * (box_width - 2) + "┘", COLOR_AMBER)
        
        # Second row: GOLD, OIL, EUR/USD
        row2 = ["GOLD", "OIL", "EUR/USD"]
        for i, sym in enumerate(row2):
            x = i * (box_width + 1) + 1
            
            # Box border top
            self.draw_text(y + 10, x, "┌" + "─" * (box_width - 2) + "┐", COLOR_AMBER)
            
            if sym in self.data:
                d = self.data[sym]
                # Symbol name
                self.draw_text(y + 11, x + 2, d["name"][:box_width-4], COLOR_CYAN, bold=True)
                
                # Price (large)
                price_str = self.format_price(d["price"])
                self.draw_text(y + 12, x + 2, f"${price_str}", COLOR_WHITE, bold=True)
                
                # Change
                color = COLOR_GREEN if d["change"] >= 0 else COLOR_RED
                arrow = "▲" if d["change"] >= 0 else "▼"
                sign = "+" if d["pct"] >= 0 else ""
                change_str = f"{arrow} {sign}{d['pct']:.2f}%"
                self.draw_text(y + 13, x + 2, change_str, color, bold=True)
            else:
                # NO DATA
                self.draw_text(y + 11, x + 2, sym, COLOR_DIM, bold=True)
                self.draw_text(y + 12, x + 2, "NO DATA", COLOR_RED, bold=True)
                self.draw_text(y + 13, x + 2, "─" * 8, COLOR_DIM)
            
            # Box border bottom
            self.draw_text(y + 14, x, "└" + "─" * (box_width - 2) + "┘", COLOR_AMBER)
        
        return 16  # Height of spotlight section
    
    def draw_table(self, y: int, title: str, symbols: List[str], width: int = 45):
        """Draw a data table"""
        # Table header
        header = f"┌─ {title} " + "─" * (width - len(title) - 4) + "┐"
        self.draw_line(y, header, COLOR_AMBER, bold=True)
        
        # Column headers
        col_header = f"│ {'Symbol':<8} {'Price (USD)':>12} {'Change':>10} {'%':>8} │"
        self.draw_line(y + 1, col_header, COLOR_DIM)
        
        # Data rows
        row_idx = 2
        for sym in symbols:
            # Symbol
            self.draw_text(y + row_idx, 0, "│ ", COLOR_AMBER)
            self.draw_text(y + row_idx, 2, sym[:8], COLOR_WHITE, bold=True)
            
            if sym in self.data:
                d = self.data[sym]
                color = COLOR_GREEN if d["change"] >= 0 else COLOR_RED
                arrow = "▲" if d["change"] >= 0 else "▼"
                sign = "+" if d["change"] >= 0 else ""
                
                price_str = self.format_price(d["price"])
                change_str = f"{sign}{d['change']:.2f}"
                pct_str = f"{sign}{d['pct']:.2f}%"
                
                # Price
                self.draw_text(y + row_idx, 11, f"${price_str:>11}", COLOR_WHITE)
                
                # Change and % in color
                self.draw_text(y + row_idx, 25, f"{arrow} {change_str:>8}", color)
                self.draw_text(y + row_idx, 36, f"{pct_str:>8}", color)
            else:
                # NO DATA
                self.draw_text(y + row_idx, 11, "  NO DATA", COLOR_RED)
            
            # Border
            self.draw_text(y + row_idx, self.width - width - 1, "│", COLOR_AMBER)
            
            row_idx += 1
        
        # Table footer
        footer = "└" + "─" * (width - 2) + "┘"
        self.draw_line(y + row_idx, footer, COLOR_AMBER, bold=True)
        
        return row_idx + 1
    
    def draw_side_by_side(self, y: int, title1: str, syms1: List[str], 
                          title2: str, syms2: List[str]):
        """Draw two tables side by side"""
        half_width = (self.width - 4) // 2
        
        # Left table header
        left_header = f"┌─ {title1} " + "─" * (half_width - len(title1) - 4) + "┐"
        self.draw_line(y, left_header, COLOR_AMBER, bold=True)
        
        # Right table header
        right_header = f"┌─ {title2} " + "─" * (half_width - len(title2) - 4) + "┐"
        self.draw_text(y, half_width + 2, right_header, COLOR_AMBER, bold=True)
        
        # Column headers
        left_cols = f"│ {'Symbol':<8} {'USD':>10} {'%':>8} │"
        right_cols = f"│ {'Symbol':<8} {'USD':>10} {'%':>8} │"
        self.draw_line(y + 1, left_cols, COLOR_DIM)
        self.draw_text(y + 1, half_width + 2, right_cols, COLOR_DIM)
        
        # Data rows
        for i in range(max(len(syms1), len(syms2))):
            row_y = y + 2 + i
            
            # Left side
            if i < len(syms1):
                sym = syms1[i]
                self.draw_text(row_y, 0, f"│ ", COLOR_AMBER)
                self.draw_text(row_y, 2, sym[:6], COLOR_WHITE, bold=True)
                
                if sym in self.data:
                    d = self.data[sym]
                    color = COLOR_GREEN if d["change"] >= 0 else COLOR_RED
                    arrow = "▲" if d["change"] >= 0 else "▼"
                    sign = "+" if d["pct"] >= 0 else ""
                    
                    self.draw_text(row_y, 9, f"${self.format_price(d['price']):>9}", COLOR_WHITE)
                    self.draw_text(row_y, 22, f"{arrow} {sign}{d['pct']:.2f}%", color)
                else:
                    self.draw_text(row_y, 9, "NO DATA", COLOR_RED)
                
                self.draw_text(row_y, half_width - 1, "│", COLOR_AMBER)
            
            # Right side
            if i < len(syms2):
                sym = syms2[i]
                self.draw_text(row_y, half_width + 1, "│ ", COLOR_AMBER)
                self.draw_text(row_y, half_width + 3, sym[:8], COLOR_WHITE, bold=True)
                
                if sym in self.data:
                    d = self.data[sym]
                    color = COLOR_GREEN if d["change"] >= 0 else COLOR_RED
                    arrow = "▲" if d["change"] >= 0 else "▼"
                    sign = "+" if d["pct"] >= 0 else ""
                    
                    self.draw_text(row_y, half_width + 12, f"${d['price']:>9}", COLOR_WHITE)
                    self.draw_text(row_y, half_width + 25, f"{arrow} {sign}{d['pct']:.2f}%", color)
                else:
                    self.draw_text(row_y, half_width + 12, "NO DATA", COLOR_RED)
                
                self.draw_text(row_y, self.width - 2, "│", COLOR_AMBER)
        
        # Footers
        left_footer = "└" + "─" * (half_width - 2) + "┘"
        right_footer = "└" + "─" * (half_width - 2) + "┘"
        last_row = y + 2 + max(len(syms1), len(syms2))
        self.draw_line(last_row, left_footer, COLOR_AMBER, bold=True)
        self.draw_text(last_row, half_width + 2, right_footer, COLOR_AMBER, bold=True)
        
        return last_row + 1
    
    def draw_messages(self, y: int):
        """Draw status messages"""
        if not self.messages:
            return y
        
        self.draw_line(y, "─" * 40, COLOR_DIM)
        for i, (ts, msg, msg_type) in enumerate(self.messages[-3:]):
            color = COLOR_GREEN if msg_type == "ok" else (COLOR_RED if msg_type == "err" else COLOR_WHITE)
            self.draw_text(y + 1 + i, 2, f"[{ts}]", COLOR_DIM)
            prefix = "OK " if msg_type == "ok" else ("ERR" if msg_type == "err" else "   ")
            self.draw_text(y + 1 + i, 12, prefix, color)
            self.draw_text(y + 1 + i, 16, msg, color)
        return y + len(self.messages[-3:]) + 1
    
    def draw_command(self, y: int):
        """Draw command input line"""
        # Command prompt
        self.draw_text(y, 0, "COMMAND> ", COLOR_AMBER, bold=True)
        
        # Current command with cursor
        curses.curs_set(1)  # Show cursor
        self.draw_text(y, 9, self.command, COLOR_WHITE, bold=True)
        
        # Position cursor
        try:
            self.screen.move(y, 9 + len(self.command))
        except:
            pass
        
        # Help text
        self.draw_text(y + 1, 2, "help | buy/sell <sym> <qty> | long/short <sym> <qty> | news | reddit | chart", COLOR_DIM)
    
    def render_trade_history(self):
        """Render the trade history view"""
        self.screen.clear()
        self.height, self.width = self.screen.getmaxyx()
        y = 0
        
        # Header
        self.draw_header(y)
        y += 5
        
        # Title
        self.draw_line(y, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        self.draw_text(y + 1, 2, "★ TRADE HISTORY ★", COLOR_YELLOW, bold=True)
        self.draw_text(y + 1, self.width - 30, "Press 'back' to return", COLOR_DIM)
        self.draw_line(y + 2, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        y += 4
        
        # Get trade summary
        summary = get_trade_summary()
        
        # Summary row
        self.draw_text(y, 2, f"Total Trades: {summary['total_trades']}", COLOR_WHITE, bold=True)
        self.draw_text(y, 30, f"Buys: {summary['total_buys']}", COLOR_GREEN)
        self.draw_text(y, 50, f"Sells: {summary['total_sells']}", COLOR_RED)
        y += 2
        
        # Table header
        header = f"│ {'ID':>4} │ {'Date/Time':<19} │ {'Symbol':<8} │ {'Side':<4} │ {'Qty':>12} │ {'Price':>12} │ {'Total':>14} │"
        self.draw_line(y, "┌" + "─" * (self.width - 3) + "┐", COLOR_AMBER)
        self.draw_line(y + 1, header[:self.width-2], COLOR_CYAN, bold=True)
        self.draw_line(y + 2, "├" + "─" * (self.width - 3) + "┤", COLOR_AMBER)
        y += 3
        
        # Get trades
        trades = get_trade_history(limit=self.height - y - 5)
        
        if not trades:
            self.draw_line(y, "│ No trades recorded yet. Use 'buy/sell <symbol> <qty>' to record trades.", COLOR_DIM)
            y += 1
        else:
            for trade in trades:
                # Truncate if needed
                row = f"│ {trade['id']:>4} │ {trade['timestamp']:<19} │ {trade['symbol']:<8} │ {trade['side']:<4} │ {trade['quantity']:>12,.4f} │ ${trade['price']:>11,.2f} │ ${trade['total']:>13,.2f} │"
                
                # Color based on side
                if trade['side'] == 'BUY':
                    color = COLOR_GREEN
                else:
                    color = COLOR_RED
                
                self.draw_text(y, 0, "│ ", COLOR_AMBER)
                self.draw_text(y, 2, f"{trade['id']:>4}", COLOR_DIM)
                self.draw_text(y, 9, f"│ {trade['timestamp']}", COLOR_WHITE)
                self.draw_text(y, 30, f"│ {trade['symbol']}", COLOR_CYAN, bold=True)
                self.draw_text(y, 41, f"│ {trade['side']}", color, bold=True)
                self.draw_text(y, 48, f"│ {trade['quantity']:,.4f}", COLOR_WHITE)
                self.draw_text(y, 63, f"│ ${trade['price']:,.2f}", COLOR_WHITE)
                self.draw_text(y, 80, f"│ ${trade['total']:,.2f}", color)
                self.draw_text(y, self.width - 3, "│", COLOR_AMBER)
                
                y += 1
                
                if y >= self.height - 4:
                    break
        
        # Table footer
        self.draw_line(y, "└" + "─" * (self.width - 3) + "┘", COLOR_AMBER)
        y += 2
        
        # Volume by symbol
        if summary['volume_by_symbol']:
            self.draw_text(y, 2, "Volume by Symbol:", COLOR_YELLOW, bold=True)
            y += 1
            vol_str = "  ".join([f"{sym}: ${vol:,.2f}" for sym, vol in list(summary['volume_by_symbol'].items())[:5]])
            self.draw_text(y, 2, vol_str[:self.width-4], COLOR_WHITE)
            y += 2
        
        # Messages
        y = self.draw_messages(y)
        y += 1
        
        # Command
        self.draw_command(y)
        
        self.screen.refresh()
    
    def render_chart(self):
        """Render the chart view"""
        self.screen.clear()
        self.height, self.width = self.screen.getmaxyx()
        y = 0
        
        # Header
        self.draw_header(y)
        y += 5
        
        # Title
        self.draw_line(y, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        self.draw_text(y + 1, 2, f"★ {self.chart_title} ★", COLOR_YELLOW, bold=True)
        self.draw_text(y + 1, self.width - 30, "Press 'back' to return", COLOR_DIM)
        self.draw_line(y + 2, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        y += 4
        
        # Render chart lines
        if self.chart_lines:
            for line in self.chart_lines:
                if y < self.height - 4:
                    # Color the chart based on content
                    if "Range:" in line or "●" in line:
                        self.draw_line(y, line[:self.width-1], COLOR_CYAN)
                    elif "$" in line and "│" in line:
                        # Price lines - green for high, red for low
                        self.draw_line(y, line[:self.width-1], COLOR_WHITE)
                    elif "─" in line or "└" in line:
                        self.draw_line(y, line[:self.width-1], COLOR_AMBER)
                    else:
                        self.draw_line(y, line[:self.width-1], COLOR_WHITE)
                    y += 1
        else:
            self.draw_line(y, "No chart data. Use 'chart <symbol> <days>' or 'compare <sym1> <sym2> <days>'", COLOR_DIM)
            y += 1
        
        # Messages
        y = self.draw_messages(max(y + 1, self.height - 6))
        
        # Command
        self.draw_command(self.height - 3)
        
        self.screen.refresh()
    
    def render_news(self):
        """Render the news headlines view"""
        self.screen.clear()
        self.height, self.width = self.screen.getmaxyx()
        y = 0
        
        # Header
        self.draw_header(y)
        y += 5
        
        # Title with category
        category_name = NEWS_SOURCES.get(self.news_category, {}).get('name', self.news_category.upper())
        source_name = "Reddit" if self.news_source == "reddit" else "RSS Feeds"
        
        self.draw_line(y, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        title = f"★ NEWS: {category_name} ({source_name}) ★"
        self.draw_text(y + 1, 2, title, COLOR_YELLOW, bold=True)
        self.draw_text(y + 1, self.width - 35, "news <category> | reddit <sub>", COLOR_DIM)
        self.draw_line(y + 2, "═" * (self.width - 1), COLOR_AMBER, bold=True)
        y += 4
        
        # Categories help
        cats = "Categories: business | stocks | crypto | politics | world"
        self.draw_text(y, 2, cats, COLOR_CYAN)
        y += 1
        reddit_cats = "Reddit: wsb | stocks | crypto | politics | economy"
        self.draw_text(y, 2, reddit_cats, COLOR_DIM)
        y += 2
        
        # Render news
        if self.news_data:
            for i, item in enumerate(self.news_data):
                if y >= self.height - 4:
                    break
                
                if self.news_source == "reddit":
                    # Reddit format
                    title = item.get('title', 'No title')[:self.width - 20]
                    score = item.get('score', 0)
                    comments = item.get('comments', 0)
                    subreddit = item.get('subreddit', '')
                    
                    # Title
                    self.draw_text(y, 2, f"{i+1}.", COLOR_DIM)
                    self.draw_text(y, 5, title, COLOR_WHITE, bold=True)
                    y += 1
                    
                    # Meta
                    meta = f"   r/{subreddit} | ↑{score} | 💬{comments}"
                    self.draw_text(y, 5, meta, COLOR_DIM)
                    y += 2
                else:
                    # RSS format
                    title = item.get('title', 'No title')[:self.width - 10]
                    source = item.get('source_name', item.get('source', 'Unknown'))
                    pub_date = item.get('pubDate', '')[:10]
                    
                    # Title
                    self.draw_text(y, 2, f"{i+1}.", COLOR_DIM)
                    self.draw_text(y, 5, title, COLOR_WHITE, bold=True)
                    y += 1
                    
                    # Source and date
                    meta = f"   {source} | {pub_date}"
                    self.draw_text(y, 5, meta, COLOR_DIM)
                    y += 2
        else:
            self.draw_line(y, "Loading news... or no data available.", COLOR_DIM)
            y += 1
            self.draw_line(y, "Use: news <category> or reddit <subreddit>", COLOR_DIM)
            y += 1
        
        # Messages
        y = self.draw_messages(max(y + 1, self.height - 6))
        
        # Command
        self.draw_command(self.height - 3)
        
        self.screen.refresh()
    
    def render(self):
        """Render the full terminal display"""
        # Check if we should render trade history view
        if self.view_mode == "history":
            self.render_trade_history()
            return
        
        # Check if we should render chart view
        if self.view_mode == "chart":
            self.render_chart()
            return
        
        # Check if we should render news view
        if self.view_mode == "news":
            self.render_news()
            return
        
        self.screen.clear()
        
        # Resize check
        self.height, self.width = self.screen.getmaxyx()
        
        y = 0
        
        # Header
        self.draw_header(y)
        y += 5
        
        # Market Spotlight (featured prices)
        y += self.draw_spotlight(y)
        y += 1
        
        # Ticker
        self.draw_ticker(y)
        y += 2
        
        # Equities table
        y = self.draw_table(y, "EQUITIES", ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "JPM", "V", "WMT", "DIS", "NFLX"])
        y += 1
        
        # Crypto & Forex side by side
        y = self.draw_side_by_side(y, "CRYPTO", ["BTC", "ETH", "SOL", "XRP", "DOGE", "ADA", "AVAX", "LINK"], 
                                      "FOREX", ["EUR/USD", "GBP/USD", "USD/JPY", "USD/CHF", "AUD/USD", "USD/CAD"])
        y += 1
        
        # Commodities & Indices side by side
        y = self.draw_side_by_side(y, "COMMODITIES", ["OIL", "GOLD", "SILVER", "NATGAS", "COPPER"],
                                      "INDICES", ["SPX", "DJI", "NDQ", "VIX", "RUT"])
        y += 1
        
        # Messages
        y = self.draw_messages(y)
        y += 1
        
        # Command
        self.draw_command(y)
        
        self.screen.refresh()
    
    def process_command(self, cmd: str):
        """Process a command"""
        cmd = cmd.strip().lower()
        parts = cmd.split()
        
        if not parts:
            return
        
        if parts[0] == "help":
            self.add_message("Commands: view, chart, compare, history, bal, spot/futures, orders, news, reddit", "info")
            self.add_message("Spot: buy/sell <sym> <qty> [price] | Futures: long/short <sym> <qty> <lev>", "info")
            self.add_message("News: news <category> | reddit <sub> | Categories: business, stocks, crypto, politics", "info")
        
        elif parts[0] == "view" and len(parts) > 1:
            sym = parts[1].upper()
            for key in self.data:
                if sym in key.upper():
                    self.focused = key
                    self.view_mode = "asset"
                    self.add_message(f"Viewing {key}", "ok")
                    return
            self.add_message(f"Not found: {sym}", "err")
        
        elif parts[0] == "back":
            self.focused = None
            self.view_mode = "main"
            self.add_message("Main view", "info")
        
        elif parts[0] == "bal":
            # Show account balances
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled. Set BINANCE_API_KEY and BINANCE_API_SECRET", "err")
                return
            
            self.add_message("Fetching balances...", "info")
            
            def fetch_balances():
                spot = get_spot_balance()
                futures = get_futures_balance()
                
                if spot:
                    usdt = next((b for b in spot if b['asset'] == 'USDT'), None)
                    if usdt:
                        self.add_message(f"Spot USDT: ${usdt['free']:,.2f} (locked: ${usdt['locked']:,.2f})", "ok")
                    else:
                        self.add_message(f"Spot: {len(spot)} assets", "ok")
                
                if futures:
                    usdt = next((b for b in futures if b['asset'] == 'USDT'), None)
                    if usdt:
                        self.add_message(f"Futures USDT: ${usdt['balance']:,.2f} (avail: ${usdt['available']:,.2f})", "ok")
                
                if not spot and not futures:
                    self.add_message("Could not fetch balances", "err")
            
            threading.Thread(target=fetch_balances, daemon=True).start()
        
        elif parts[0] == "refresh":
            self.add_message("Refreshing market data...", "info")
            try:
                real_data = get_quick_prices()
                if real_data:
                    self.data.update(real_data)
                    self.add_message(f"Updated {len(real_data)} prices", "ok")
                else:
                    self.add_message("API rate limited, try later", "err")
            except Exception:
                self.add_message("Refresh failed", "err")
        
        elif parts[0] in ["buy", "sell"]:
            # Spot trading: buy/sell <symbol> <quantity> [price]
            # If price provided = limit order, otherwise = market order (if trading enabled) or local record
            if len(parts) >= 3:
                try:
                    symbol = parts[1].upper()
                    quantity = float(parts[2])
                    price = float(parts[3]) if len(parts) >= 4 else None
                    
                    # Ensure symbol has USDT suffix for Binance
                    if not symbol.endswith('USDT'):
                        symbol = symbol + 'USDT'
                    
                    if TRADING_ENABLED:
                        # Execute real trade on Binance
                        self.add_message(f"Executing {parts[0].upper()} {quantity} {symbol}...", "info")
                        
                        def execute_spot_trade():
                            if price:
                                # Limit order
                                if parts[0] == 'buy':
                                    result = spot_limit_buy(symbol, quantity, price)
                                else:
                                    result = spot_limit_sell(symbol, quantity, price)
                            else:
                                # Market order
                                if parts[0] == 'buy':
                                    result = spot_market_buy(symbol, quantity)
                                else:
                                    result = spot_market_sell(symbol, quantity)
                            
                            if result and 'orderId' in result:
                                self.add_message(f"Order placed! ID: {result['orderId']}", "ok")
                                # Also record locally
                                exec_price = price if price else self.data.get(symbol.replace('USDT', ''), {}).get('price', 0)
                                if exec_price:
                                    record_trade(symbol, parts[0].upper(), quantity, exec_price)
                            elif result and result.get('error'):
                                self.add_message(f"Error: {result.get('message', 'Unknown error')[:50]}", "err")
                            else:
                                self.add_message("Order failed", "err")
                        
                        threading.Thread(target=execute_spot_trade, daemon=True).start()
                    else:
                        # Local record only
                        if price:
                            total = quantity * price
                            trade_id = record_trade(symbol, parts[0].upper(), quantity, price)
                            self.add_message(f"[LOCAL] {parts[0].upper()} {quantity} {symbol} @ ${price:,.2f} = ${total:,.2f} (ID: {trade_id})", "ok")
                        else:
                            # Get current price from data
                            base_symbol = symbol.replace('USDT', '')
                            if base_symbol in self.data:
                                price = self.data[base_symbol]['price']
                            elif symbol in self.data:
                                price = self.data[symbol]['price']
                            else:
                                self.add_message(f"Symbol not found: {symbol}", "err")
                                return
                            
                            total = quantity * price
                            trade_id = record_trade(symbol, parts[0].upper(), quantity, price)
                            self.add_message(f"[LOCAL] {parts[0].upper()} {quantity} {symbol} @ ${price:,.2f} = ${total:,.2f} (ID: {trade_id})", "ok")
                    
                except ValueError:
                    self.add_message("Invalid quantity or price", "err")
            else:
                self.add_message(f"Usage: {parts[0]} <symbol> <quantity> [price]", "err")
        
        elif parts[0] in ["history", "trades"]:
            self.view_mode = "history"
            self.add_message("Viewing trade history", "info")
        
        elif parts[0] == "positions":
            # Show open futures positions
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled", "err")
                return
            
            def fetch_positions():
                positions = get_futures_positions()
                if positions:
                    for p in positions[:5]:
                        pnl_str = f"+${p['unrealized_pnl']:,.2f}" if p['unrealized_pnl'] >= 0 else f"-${abs(p['unrealized_pnl']):,.2f}"
                        self.add_message(f"{p['symbol']} {p['side']} {abs(p['position_amt'])} @ ${p['entry_price']:,.2f} | PnL: {pnl_str}", "ok")
                    if len(positions) > 5:
                        self.add_message(f"... and {len(positions) - 5} more positions", "info")
                else:
                    self.add_message("No open positions", "info")
            
            threading.Thread(target=fetch_positions, daemon=True).start()
        
        elif parts[0] == "orders":
            # Show open orders: orders [symbol] [-f for futures]
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled", "err")
                return
            
            symbol = parts[1].upper() if len(parts) > 1 and not parts[1].startswith('-') else None
            futures = '-f' in parts or '--futures' in parts
            
            if symbol and not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            
            def fetch_orders():
                orders = get_open_orders(symbol, futures=futures)
                if orders:
                    for o in orders[:5]:
                        self.add_message(f"{o['symbol']} {o['side']} {o['quantity']} @ ${o['price']:,.2f} | ID: {o['order_id']}", "ok")
                    if len(orders) > 5:
                        self.add_message(f"... and {len(orders) - 5} more orders", "info")
                else:
                    self.add_message("No open orders", "info")
            
            threading.Thread(target=fetch_orders, daemon=True).start()
        
        elif parts[0] == "cancel":
            # Cancel order: cancel <symbol> <order_id> [-f for futures]
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled", "err")
                return
            
            if len(parts) >= 3:
                symbol = parts[1].upper()
                if not symbol.endswith('USDT'):
                    symbol = symbol + 'USDT'
                
                try:
                    order_id = int(parts[2])
                    futures = '-f' in parts or '--futures' in parts
                    
                    result = cancel_order(symbol, order_id, futures=futures)
                    if result and 'orderId' in result:
                        self.add_message(f"Cancelled order #{order_id}", "ok")
                    else:
                        self.add_message(f"Failed to cancel: {result.get('message', 'Unknown')[:40]}", "err")
                except ValueError:
                    self.add_message("Invalid order ID", "err")
            else:
                self.add_message("Usage: cancel <symbol> <order_id> [-f]", "err")
        
        elif parts[0] in ["long", "short"]:
            # Futures trading: long/short <symbol> <quantity> <leverage>
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled. Set BINANCE_API_KEY and BINANCE_API_SECRET", "err")
                return
            
            if len(parts) >= 3:
                symbol = parts[1].upper()
                if not symbol.endswith('USDT'):
                    symbol = symbol + 'USDT'
                
                try:
                    quantity = float(parts[2])
                    leverage = int(parts[3]) if len(parts) >= 4 else 1
                    
                    if leverage < 1 or leverage > 125:
                        self.add_message("Leverage must be 1-125", "err")
                        return
                    
                    self.add_message(f"Opening {parts[0]} {symbol} x{leverage}...", "info")
                    
                    def execute_futures_trade():
                        if parts[0] == 'long':
                            result = futures_market_long(symbol, quantity, leverage)
                        else:
                            result = futures_market_short(symbol, quantity, leverage)
                        
                        if result and 'orderId' in result:
                            self.add_message(f"Futures {parts[0].upper()} placed! ID: {result['orderId']}", "ok")
                        elif result and result.get('error'):
                            self.add_message(f"Error: {result.get('message', 'Unknown error')[:50]}", "err")
                        else:
                            self.add_message("Order failed", "err")
                    
                    threading.Thread(target=execute_futures_trade, daemon=True).start()
                except ValueError:
                    self.add_message("Invalid quantity or leverage", "err")
            else:
                self.add_message(f"Usage: {parts[0]} <symbol> <quantity> [leverage]", "err")
        
        elif parts[0] == "close":
            # Close futures position: close <symbol>
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled", "err")
                return
            
            if len(parts) >= 2:
                symbol = parts[1].upper()
                if not symbol.endswith('USDT'):
                    symbol = symbol + 'USDT'
                
                self.add_message(f"Closing {symbol} position...", "info")
                
                def close_pos():
                    result = futures_close_position(symbol)
                    if result and 'orderId' in result:
                        self.add_message(f"Position closed! Order ID: {result['orderId']}", "ok")
                    elif result and result.get('error'):
                        self.add_message(f"Error: {result.get('message', 'Unknown')[:40]}", "err")
                    else:
                        self.add_message("Could not close position", "err")
                
                threading.Thread(target=close_pos, daemon=True).start()
            else:
                self.add_message("Usage: close <symbol>", "err")
        
        elif parts[0] == "leverage":
            # Set leverage: leverage <symbol> <leverage>
            if not TRADING_ENABLED:
                self.add_message("Trading not enabled", "err")
                return
            
            if len(parts) >= 3:
                symbol = parts[1].upper()
                if not symbol.endswith('USDT'):
                    symbol = symbol + 'USDT'
                
                try:
                    leverage = int(parts[2])
                    result = set_leverage(symbol, leverage)
                    if result and 'leverage' in result:
                        self.add_message(f"{symbol} leverage set to {leverage}x", "ok")
                    else:
                        self.add_message(f"Failed to set leverage", "err")
                except ValueError:
                    self.add_message("Invalid leverage value", "err")
            else:
                self.add_message("Usage: leverage <symbol> <1-125>", "err")
        
        elif parts[0] == "delete" and len(parts) > 1:
            try:
                trade_id = int(parts[1])
                if delete_trade(trade_id):
                    self.add_message(f"Deleted trade #{trade_id}", "ok")
                else:
                    self.add_message(f"Trade #{trade_id} not found", "err")
            except ValueError:
                self.add_message("Invalid trade ID", "err")
        
        elif parts[0] == "chart":
            # chart <symbol> <days> - Show price chart
            # chart <symbol> <start_date> <end_date> - Show price chart for date range
            if len(parts) >= 3:
                symbol = parts[1].upper()
                
                # Check if it's a date range or just days
                if len(parts) >= 4:
                    # Date range mode: chart BTC 2024-01-01 2024-03-01
                    start_date = parts[2]
                    end_date = parts[3]
                    self.add_message(f"Fetching {symbol} from {start_date} to {end_date}...", "info")
                    
                    # Fetch in background to not block
                    def fetch_range():
                        data = get_historical_range(symbol, start_date, end_date)
                        if data:
                            chart = PriceChart(self.width, 25)
                            self.chart_lines = chart.render_ascii(data, f"{symbol} Price Chart")
                            self.chart_title = f"{symbol}: {start_date} to {end_date}"
                            self.view_mode = "chart"
                            self.add_message(f"Loaded {len(data)} data points for {symbol}", "ok")
                        else:
                            self.add_message(f"Could not fetch data for {symbol}", "err")
                    
                    thread = threading.Thread(target=fetch_range, daemon=True)
                    thread.start()
                else:
                    # Days mode: chart BTC 30
                    try:
                        days = int(parts[2])
                        self.add_message(f"Fetching {symbol} for {days} days...", "info")
                        
                        def fetch_days():
                            data = get_historical_prices(symbol, days)
                            if data:
                                chart = PriceChart(self.width, 25)
                                self.chart_lines = chart.render_ascii(data, f"{symbol} Price Chart ({days} days)")
                                self.chart_title = f"{symbol} - {days} Day History"
                                self.view_mode = "chart"
                                self.add_message(f"Loaded {len(data)} data points for {symbol}", "ok")
                            else:
                                self.add_message(f"Could not fetch data for {symbol}", "err")
                        
                        thread = threading.Thread(target=fetch_days, daemon=True)
                        thread.start()
                    except ValueError:
                        self.add_message("Usage: chart <symbol> <days> OR chart <symbol> <start> <end>", "err")
            else:
                self.add_message("Usage: chart <symbol> <days> OR chart <symbol> <start_date> <end_date>", "err")
        
        elif parts[0] == "compare":
            # compare <sym1> <sym2> <days> - Compare two assets
            # compare <sym1> <sym2> <start> <end> - Compare for date range
            if len(parts) >= 4:
                sym1 = parts[1].upper()
                sym2 = parts[2].upper()
                
                if len(parts) >= 5:
                    # Date range mode
                    start_date = parts[3]
                    end_date = parts[4]
                    self.add_message(f"Fetching {sym1} vs {sym2} from {start_date} to {end_date}...", "info")
                    
                    def fetch_compare_range():
                        data1 = get_historical_range(sym1, start_date, end_date)
                        data2 = get_historical_range(sym2, start_date, end_date)
                        
                        if data1 and data2:
                            chart = PriceChart(self.width, 25)
                            datasets = [(sym1, data1), (sym2, data2)]
                            self.chart_lines = chart.render_percentage_change(datasets, f"{sym1} vs {sym2}")
                            self.chart_title = f"{sym1} vs {sym2} Comparison"
                            self.view_mode = "chart"
                            self.add_message(f"Loaded comparison: {len(data1)} + {len(data2)} points", "ok")
                        else:
                            missing = []
                            if not data1: missing.append(sym1)
                            if not data2: missing.append(sym2)
                            self.add_message(f"Could not fetch data for: {', '.join(missing)}", "err")
                    
                    thread = threading.Thread(target=fetch_compare_range, daemon=True)
                    thread.start()
                else:
                    # Days mode
                    try:
                        days = int(parts[3])
                        self.add_message(f"Fetching {sym1} vs {sym2} for {days} days...", "info")
                        
                        def fetch_compare():
                            data1 = get_historical_prices(sym1, days)
                            data2 = get_historical_prices(sym2, days)
                            
                            if data1 and data2:
                                chart = PriceChart(self.width, 25)
                                datasets = [(sym1, data1), (sym2, data2)]
                                self.chart_lines = chart.render_percentage_change(datasets, f"{sym1} vs {sym2}")
                                self.chart_title = f"{sym1} vs {sym2} - {days} Days"
                                self.view_mode = "chart"
                                self.add_message(f"Loaded comparison: {len(data1)} + {len(data2)} points", "ok")
                            else:
                                missing = []
                                if not data1: missing.append(sym1)
                                if not data2: missing.append(sym2)
                                self.add_message(f"Could not fetch data for: {', '.join(missing)}", "err")
                        
                        thread = threading.Thread(target=fetch_compare, daemon=True)
                        thread.start()
                    except ValueError:
                        self.add_message("Usage: compare <sym1> <sym2> <days>", "err")
            else:
                self.add_message("Usage: compare <sym1> <sym2> <days> OR compare <sym1> <sym2> <start> <end>", "err")
        
        elif parts[0] == "news":
            # News command: news [category]
            # Categories: business, stocks, crypto, politics, world
            category = parts[1].lower() if len(parts) > 1 else "business"
            
            valid_categories = ['business', 'stocks', 'crypto', 'politics', 'world']
            if category not in valid_categories:
                self.add_message(f"Invalid category. Use: {', '.join(valid_categories)}", "err")
                return
            
            self.news_category = category
            self.news_source = "rss"
            self.add_message(f"Fetching {category} news...", "info")
            
            def fetch_news():
                news = get_news(category)
                if news:
                    self.news_data = news
                    self.view_mode = "news"
                    self.add_message(f"Loaded {len(news)} headlines", "ok")
                else:
                    self.add_message("Could not fetch news. Try again later.", "err")
            
            threading.Thread(target=fetch_news, daemon=True).start()
        
        elif parts[0] == "reddit":
            # Reddit command: reddit [subreddit]
            # Subreddits: stocks, wallstreetbets, crypto, politics, economy
            subreddit = parts[1].lower() if len(parts) > 1 else "stocks"
            
            # Map shortcuts
            subreddit_map = {
                'wsb': 'wallstreetbets',
                'wallstreetbets': 'wallstreetbets',
                'stocks': 'stocks',
                'crypto': 'crypto',
                'politics': 'politics',
                'economy': 'economy',
            }
            
            subreddit = subreddit_map.get(subreddit, subreddit)
            
            if subreddit not in REDDIT_SOURCES:
                self.add_message(f"Invalid subreddit. Use: stocks, wsb, crypto, politics, economy", "err")
                return
            
            self.news_category = subreddit
            self.news_source = "reddit"
            self.add_message(f"Fetching r/{subreddit} posts...", "info")
            
            def fetch_reddit():
                posts = get_reddit_news(subreddit)
                if posts:
                    self.news_data = posts
                    self.view_mode = "news"
                    self.add_message(f"Loaded {len(posts)} posts", "ok")
                else:
                    self.add_message("Could not fetch Reddit posts. Try again later.", "err")
            
            threading.Thread(target=fetch_reddit, daemon=True).start()
        
        else:
            self.add_message(f"Unknown: {parts[0]}", "err")
    
    def handle_input(self) -> bool:
        """Handle keyboard input. Returns False if should quit."""
        try:
            ch = self.screen.getch()
        except:
            return True
        
        if ch == -1:  # No input
            return True
        
        # Ctrl+C - always exit
        if ch == 3:
            return False
        
        # Enter - execute command
        if ch == ord('\n') or ch == ord('\r'):
            if self.command.strip():
                self.process_command(self.command)
            self.command = ""
            return True
        
        # Escape - clear command or go back
        elif ch == 27:
            self.command = ""
            if self.view_mode == "history" or self.view_mode == "chart":
                self.view_mode = "main"
            return True
        
        # Backspace
        elif ch == 127 or ch == 8 or ch == curses.KEY_BACKSPACE:
            self.command = self.command[:-1]
            return True
        
        # Printable characters (including H)
        elif 32 <= ch <= 126:
            # H key - only toggle history if command buffer is empty
            if (ch == ord('H') or ch == ord('h')) and len(self.command) == 0:
                if self.view_mode == "history":
                    self.view_mode = "main"
                    self.add_message("Main view", "info")
                else:
                    self.view_mode = "history"
                    self.add_message("Trade history view", "info")
            else:
                # Add character to command
                self.command += chr(ch)
            return True
        
        return True
    
    def run(self):
        """Main run loop"""
        # Initial render
        self.render()
        
        update_counter = 0
        self._fetching = False  # Use instance variable instead of nonlocal
        
        while self.running:
            # Handle input (instant, non-blocking)
            if not self.handle_input():
                self.running = False
                break
            
            # Re-render on every iteration for instant response
            self.render()
            
            # Fetch real data periodically - but don't block!
            update_counter += 1
            if update_counter >= 150 and not self._fetching:  # ~3 seconds
                self._fetching = True
                
                def fetch_data():
                    """Fetch data in background thread"""
                    try:
                        new_data = get_quick_prices()
                        if new_data:
                            self.data.update(new_data)
                            self.last_fetch_time = datetime.now()
                            
                            crypto_count = sum(1 for k in new_data if k in ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK'])
                            if crypto_count >= 6:
                                self.api_status = "LIVE"
                            elif crypto_count > 0:
                                self.api_status = "PARTIAL"
                            else:
                                self.api_status = "ERROR"
                        else:
                            self.api_status = "ERROR"
                    except Exception:
                        self.api_status = "ERROR"
                    finally:
                        self._fetching = False
                
                # Start background thread
                import threading
                thread = threading.Thread(target=fetch_data, daemon=True)
                thread.start()
                
                update_counter = 0
            
            # Small sleep to prevent CPU spin
            time.sleep(0.02)


def main(stdscr):
    """Main entry point for curses"""
    terminal = BloombergTerminal(stdscr)
    terminal.run()


if __name__ == "__main__":
    curses.wrapper(main)

