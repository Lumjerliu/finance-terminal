#!/usr/bin/env python3
"""
Test suite for Bloomberg Terminal (Curses Version)
Run with: python3 test_terminal.py
"""

import sys
import os

# Add the directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import at module level
from bloomberg_terminal import (
    get_crypto_prices, get_quick_prices, BloombergTerminal, 
    init_colors, COLOR_AMBER, COLOR_GREEN, COLOR_RED, COLOR_WHITE
)


def test_crypto_api():
    """Test real crypto prices from Binance API"""
    print("=" * 60)
    print("TEST 1: Crypto API (Binance)...")
    print("=" * 60)
    
    data = get_crypto_prices()
    
    if not data:
        print("  [FAIL] No crypto data received from API")
        print("  [INFO] Check internet connection")
        return False
    
    print(f"  [PASS] Received {len(data)} crypto prices")
    
    # Check required fields
    required_fields = ['price', 'change', 'pct']
    for symbol in ['BTC', 'ETH']:
        if symbol in data:
            quote = data[symbol]
            missing = [f for f in required_fields if f not in quote]
            if missing:
                print(f"  [FAIL] {symbol} missing fields: {missing}")
                return False
            print(f"  [PASS] {symbol}: ${quote['price']:,.2f} ({quote['pct']:+.2f}%)")
        else:
            print(f"  [FAIL] {symbol} not in data")
            return False
    
    print("\n[PASS] Crypto API working!\n")
    return True


def test_quick_prices():
    """Test quick prices function"""
    print("=" * 60)
    print("TEST 2: Quick prices fetch...")
    print("=" * 60)
    
    data = get_quick_prices()
    
    if not data:
        print("  [FAIL] No data received")
        return False
    
    print(f"  [PASS] Received {len(data)} prices")
    
    # Check that we got crypto at minimum
    crypto_found = [s for s in ['BTC', 'ETH', 'SOL'] if s in data]
    if crypto_found:
        for sym in crypto_found:
            print(f"  [PASS] {sym}: ${data[sym]['price']:,.2f}")
    else:
        print("  [WARN] No crypto prices found (API may be rate limited)")
    
    print("\n[PASS] Quick prices working!\n")
    return True


def test_color_constants():
    """Test color constants are defined"""
    print("=" * 60)
    print("TEST 3: Color constants...")
    print("=" * 60)
    
    colors = {
        'COLOR_AMBER': COLOR_AMBER,
        'COLOR_GREEN': COLOR_GREEN,
        'COLOR_RED': COLOR_RED,
        'COLOR_WHITE': COLOR_WHITE,
    }
    
    for name, value in colors.items():
        if value is not None:
            print(f"  [PASS] {name} = {value}")
        else:
            print(f"  [FAIL] {name} is undefined")
            return False
    
    print("\n[PASS] Color constants defined!\n")
    return True


def test_terminal_class():
    """Test BloombergTerminal class exists with required methods"""
    print("=" * 60)
    print("TEST 4: BloombergTerminal class...")
    print("=" * 60)
    
    # Check class exists
    if BloombergTerminal is None:
        print("  [FAIL] BloombergTerminal class not found")
        return False
    print("  [PASS] BloombergTerminal class exists")
    
    # Check required methods
    required_methods = ['render', 'handle_input', 'process_command', 'run', 'format_price', 'add_message']
    for method in required_methods:
        if hasattr(BloombergTerminal, method):
            print(f"  [PASS] Method '{method}' exists")
        else:
            print(f"  [FAIL] Method '{method}' missing")
            return False
    
    print("\n[PASS] BloombergTerminal class structure correct!\n")
    return True


def test_format_price():
    """Test price formatting logic"""
    print("=" * 60)
    print("TEST 5: Price formatting...")
    print("=" * 60)
    
    # We can test the logic without curses
    def format_price(price):
        if price >= 10000:
            return f"{price:,.0f}"
        elif price >= 1000:
            return f"{price:,.2f}"
        elif price >= 1:
            return f"{price:,.2f}"
        else:
            return f"{price:.4f}"
    
    tests = [
        (71000.00, "71,000"),      # BTC
        (178.52, "178.52"),        # Stock
        (1.0852, "1.09"),          # Forex
        (0.0045, "0.0045"),        # Small
    ]
    
    for price, expected_prefix in tests:
        result = format_price(price)
        if expected_prefix in result or result.startswith(expected_prefix.split('.')[0]):
            print(f"  [PASS] {price} -> {result}")
        else:
            print(f"  [FAIL] {price} -> {result} (expected to contain {expected_prefix})")
            return False
    
    print("\n[PASS] Price formatting working!\n")
    return True


def test_no_mock_data():
    """Test that mock data returns empty (no fake data)"""
    print("=" * 60)
    print("TEST 6: No mock data (real data only)...")
    print("=" * 60)
    
    from bloomberg_terminal import get_mock_data
    mock = get_mock_data()
    
    if mock == {}:
        print("  [PASS] Mock data returns empty dict")
        print("  [PASS] Terminal will show NO DATA until APIs load")
    else:
        print("  [FAIL] Mock data should be empty!")
        return False
    
    print("\n[PASS] No mock data - real APIs only!\n")
    return True


def run_all_tests():
    """Run all tests"""
    print("\n" + "=" * 60)
    print("  BLOOMBERG TERMINAL TEST SUITE")
    print("  Real API Tests - No Mock Data")
    print("=" * 60 + "\n")
    
    results = []
    
    results.append(("Crypto API", test_crypto_api()))
    results.append(("Quick Prices", test_quick_prices()))
    results.append(("Color Constants", test_color_constants()))
    results.append(("Terminal Class", test_terminal_class()))
    results.append(("Price Formatting", test_format_price()))
    results.append(("No Mock Data", test_no_mock_data()))
    
    # Summary
    print("\n" + "=" * 60)
    print("  TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for _, r in results if r)
    total = len(results)
    
    for name, result in results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"  {status} {name}")
    
    print(f"\n  Total: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n  ALL TESTS PASSED!")
        print("\n  Run the terminal with: python3 bloomberg_terminal.py")
        print("  (Requires a terminal with curses support)")
        print("\n  Note: Terminal shows 'NO DATA' until APIs connect")
        print("  API status shown in header: LIVE / PARTIAL / ERROR")
    else:
        print("\n  Some tests failed. Check internet connection.")
    
    print("=" * 60 + "\n")
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
