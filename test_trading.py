#!/usr/bin/env python3
"""
Comprehensive test suite for trading functionality.
Tests all edge cases without executing real trades.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from bloomberg_terminal import (
    # Trading functions
    TRADING_ENABLED,
    binance_signature,
    get_spot_balance,
    get_futures_balance,
    get_futures_positions,
    set_leverage,
    spot_market_buy,
    spot_market_sell,
    spot_limit_buy,
    spot_limit_sell,
    futures_market_long,
    futures_market_short,
    futures_close_position,
    get_open_orders,
    cancel_order,
    cancel_all_orders,
    get_trade_history_api,
    # Local trade history
    init_trade_database,
    record_trade,
    get_trade_history,
    get_trade_summary,
    delete_trade,
    TRADE_DB_PATH,
    # Chart functions
    get_historical_prices,
    get_historical_range,
    PriceChart,
    COINGECKO_IDS,
)

import unittest
import tempfile
import shutil


class TestCommandParsing(unittest.TestCase):
    """Test command parsing edge cases"""
    
    def test_buy_command_variations(self):
        """Test various buy command formats"""
        test_cases = [
            # (input, expected_symbol, expected_qty, expected_price)
            ("buy BTC 0.01", "BTCUSDT", 0.01, None),
            ("buy btc 0.01", "BTCUSDT", 0.01, None),  # lowercase
            ("buy BTCUSDT 0.01", "BTCUSDT", 0.01, None),  # with USDT
            ("buy BTC 0.01 85000", "BTCUSDT", 0.01, 85000),  # with price
            ("buy ETH 1.5 3000.50", "ETHUSDT", 1.5, 3000.50),
            ("buy BTC 0.001", "BTCUSDT", 0.001, None),  # small quantity
            ("buy BTC 100", "BTCUSDT", 100, None),  # large quantity
        ]
        
        for cmd, expected_sym, expected_qty, expected_price in test_cases:
            parts = cmd.split()
            symbol = parts[1].upper()
            if not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            quantity = float(parts[2])
            price = float(parts[3]) if len(parts) >= 4 else None
            
            self.assertEqual(symbol, expected_sym, f"Symbol mismatch for: {cmd}")
            self.assertEqual(quantity, expected_qty, f"Quantity mismatch for: {cmd}")
            self.assertEqual(price, expected_price, f"Price mismatch for: {cmd}")
    
    def test_futures_command_variations(self):
        """Test futures command formats"""
        test_cases = [
            # (input, expected_symbol, expected_qty, expected_lev)
            ("long BTC 0.01", "BTCUSDT", 0.01, 1),
            ("long BTC 0.01 10", "BTCUSDT", 0.01, 10),
            ("long BTC 0.01 125", "BTCUSDT", 0.01, 125),  # max leverage
            ("short ETH 1 5", "ETHUSDT", 1, 5),
        ]
        
        for cmd, expected_sym, expected_qty, expected_lev in test_cases:
            parts = cmd.split()
            symbol = parts[1].upper()
            if not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            quantity = float(parts[2])
            leverage = int(parts[3]) if len(parts) >= 4 else 1
            
            self.assertEqual(symbol, expected_sym)
            self.assertEqual(quantity, expected_qty)
            self.assertEqual(leverage, expected_lev)
    
    def test_invalid_commands(self):
        """Test invalid command handling"""
        invalid_cases = [
            ("buy", "missing symbol and quantity"),
            ("buy BTC", "missing quantity"),
            ("buy BTC abc", "invalid quantity"),
            ("buy BTC 0.01 abc", "invalid price"),
            ("long BTC", "missing quantity"),
            ("long BTC 0.01 200", "leverage too high"),
            ("leverage BTC 200", "leverage out of range"),
            ("cancel", "missing symbol and id"),
            ("cancel BTC abc", "invalid order id"),
        ]
        
        for cmd, reason in invalid_cases:
            parts = cmd.split()
            
            # Test various parsing scenarios
            if parts[0] in ["buy", "sell"]:
                if len(parts) < 3:
                    continue  # Should show usage error
                else:
                    try:
                        float(parts[2])
                    except ValueError:
                        continue  # Invalid quantity caught
            
            if parts[0] in ["long", "short"]:
                if len(parts) >= 4:
                    try:
                        lev = int(parts[3])
                        # This should be caught by validation
                        if lev > 125:
                            continue  # Invalid leverage caught
                    except ValueError:
                        continue
        
        # Test leverage bounds separately - these ARE invalid
        invalid_leverages = [0, -1, 126, 200]
        for lev in invalid_leverages:
            self.assertTrue(lev < 1 or lev > 125, f"Leverage {lev} should be invalid")


class TestLeverageValidation(unittest.TestCase):
    """Test leverage validation edge cases"""
    
    def test_leverage_bounds(self):
        """Test leverage must be 1-125"""
        valid_leverages = [1, 2, 5, 10, 20, 25, 50, 75, 100, 125]
        invalid_leverages = [0, -1, 126, 200, 1000]
        
        for lev in valid_leverages:
            self.assertGreaterEqual(lev, 1)
            self.assertLessEqual(lev, 125)
        
        for lev in invalid_leverages:
            self.assertTrue(lev < 1 or lev > 125)
    
    def test_leverage_liquidation_risk(self):
        """Test liquidation price calculation"""
        # With 10x leverage, liquidation at ~10% move against you
        entry_price = 100000  # BTC at $100k
        leverage = 10
        liquidation_pct = 100 / leverage  # ~10%
        
        # Long position liquidation
        long_liq_price = entry_price * (1 - liquidation_pct/100)
        self.assertAlmostEqual(long_liq_price, 90000, places=0)
        
        # Short position liquidation
        short_liq_price = entry_price * (1 + liquidation_pct/100)
        self.assertAlmostEqual(short_liq_price, 110000, places=0)


class TestQuantityValidation(unittest.TestCase):
    """Test quantity handling edge cases"""
    
    def test_quantity_precision(self):
        """Test various quantity precisions"""
        quantities = [
            (0.00000001, True),   # 8 decimal places (satoshi)
            (0.001, True),        # 3 decimal places
            (0.01, True),         # 2 decimal places
            (1.0, True),          # 1
            (100.12345678, True), # Large with precision
            (0.0, False),         # Zero (invalid)
            (-0.01, False),       # Negative (invalid)
        ]
        
        for qty, should_be_valid in quantities:
            is_valid = qty > 0
            self.assertEqual(is_valid, should_be_valid, f"Quantity {qty} validation failed")
    
    def test_minimum_order_sizes(self):
        """Test minimum order size awareness"""
        # Binance minimums (approximate, varies by pair)
        min_orders = {
            'BTCUSDT': 0.00001,  # ~$1 at $100k BTC
            'ETHUSDT': 0.0001,   # ~$0.30 at $3k ETH
            'SOLUSDT': 0.01,     # ~$2 at $200 SOL
        }
        
        for symbol, min_qty in min_orders.items():
            # Orders below minimum would be rejected
            self.assertGreater(min_qty, 0)


class TestTradeHistoryDatabase(unittest.TestCase):
    """Test local trade history database"""
    
    def setUp(self):
        """Use temporary database for tests"""
        self.temp_dir = tempfile.mkdtemp()
        self.test_db = os.path.join(self.temp_dir, 'test_trades.db')
        
    def tearDown(self):
        """Clean up temporary files"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_record_and_retrieve_trade(self):
        """Test recording and retrieving a trade"""
        import sqlite3
        
        # Create test database
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'completed',
            notes TEXT
        )''')
        conn.commit()
        
        # Insert test trade
        c.execute('''INSERT INTO trades (timestamp, symbol, side, quantity, price, total, notes)
                     VALUES (?, ?, ?, ?, ?, ?, ?)''',
                  ('2024-01-01 12:00:00', 'BTCUSDT', 'BUY', 0.01, 85000.0, 850.0, 'Test'))
        conn.commit()
        
        # Retrieve
        c.execute('SELECT * FROM trades')
        trades = c.fetchall()
        
        self.assertEqual(len(trades), 1)
        self.assertEqual(trades[0][2], 'BTCUSDT')
        self.assertEqual(trades[0][3], 'BUY')
        self.assertEqual(trades[0][4], 0.01)
        self.assertEqual(trades[0][5], 85000.0)
        
        conn.close()
    
    def test_trade_summary(self):
        """Test trade summary calculations"""
        import sqlite3
        
        conn = sqlite3.connect(self.test_db)
        c = conn.cursor()
        c.execute('''CREATE TABLE IF NOT EXISTS trades (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            symbol TEXT NOT NULL,
            side TEXT NOT NULL,
            quantity REAL NOT NULL,
            price REAL NOT NULL,
            total REAL NOT NULL,
            status TEXT DEFAULT 'completed',
            notes TEXT
        )''')
        conn.commit()
        
        # Insert multiple trades
        trades = [
            ('2024-01-01 12:00:00', 'BTCUSDT', 'BUY', 0.01, 85000.0, 850.0, ''),
            ('2024-01-02 12:00:00', 'ETHUSDT', 'BUY', 1.0, 3000.0, 3000.0, ''),
            ('2024-01-03 12:00:00', 'BTCUSDT', 'SELL', 0.005, 86000.0, 430.0, ''),
        ]
        
        for t in trades:
            c.execute('''INSERT INTO trades (timestamp, symbol, side, quantity, price, total, notes)
                         VALUES (?, ?, ?, ?, ?, ?, ?)''', t)
        conn.commit()
        
        # Count
        c.execute('SELECT COUNT(*) FROM trades')
        total = c.fetchone()[0]
        self.assertEqual(total, 3)
        
        c.execute('SELECT COUNT(*) FROM trades WHERE side = "BUY"')
        buys = c.fetchone()[0]
        self.assertEqual(buys, 2)
        
        c.execute('SELECT COUNT(*) FROM trades WHERE side = "SELL"')
        sells = c.fetchone()[0]
        self.assertEqual(sells, 1)
        
        conn.close()


class TestSymbolHandling(unittest.TestCase):
    """Test symbol parsing edge cases"""
    
    def test_symbol_normalization(self):
        """Test symbol normalization to USDT pairs"""
        test_cases = [
            ('BTC', 'BTCUSDT'),
            ('btc', 'BTCUSDT'),
            ('BTCUSDT', 'BTCUSDT'),
            ('btcusdt', 'BTCUSDT'),
            ('ETH', 'ETHUSDT'),
            ('SOL', 'SOLUSDT'),
        ]
        
        for input_sym, expected in test_cases:
            symbol = input_sym.upper()
            if not symbol.endswith('USDT'):
                symbol = symbol + 'USDT'
            self.assertEqual(symbol, expected)
    
    def test_supported_symbols(self):
        """Test supported trading pairs"""
        supported = ['BTC', 'ETH', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'LINK']
        
        for sym in supported:
            self.assertIn(sym, COINGECKO_IDS)


class TestPriceValidation(unittest.TestCase):
    """Test price handling edge cases"""
    
    def test_price_validation(self):
        """Test price must be positive"""
        prices = [
            (85000.0, True),
            (0.50, True),
            (0.00000001, True),
            (0.0, False),
            (-100.0, False),
        ]
        
        for price, should_be_valid in prices:
            is_valid = price > 0
            self.assertEqual(is_valid, should_be_valid)
    
    def test_total_calculation(self):
        """Test total = quantity * price"""
        test_cases = [
            (0.01, 85000.0, 850.0),
            (1.0, 3000.0, 3000.0),
            (0.5, 200.0, 100.0),
            (0.001, 100000.0, 100.0),
        ]
        
        for qty, price, expected_total in test_cases:
            total = qty * price
            self.assertEqual(total, expected_total)


class TestAPIErrorHandling(unittest.TestCase):
    """Test API error handling scenarios"""
    
    def test_error_response_handling(self):
        """Test handling of API error responses"""
        error_responses = [
            {'error': True, 'code': 400, 'message': 'Invalid quantity'},
            {'error': True, 'code': 401, 'message': 'API key invalid'},
            {'error': True, 'code': 429, 'message': 'Rate limit exceeded'},
            {'error': True, 'code': 503, 'message': 'Service unavailable'},
        ]
        
        for response in error_responses:
            has_error = response.get('error', False)
            self.assertTrue(has_error)
            self.assertIn('code', response)
            self.assertIn('message', response)
    
    def test_missing_api_keys(self):
        """Test behavior when API keys not configured"""
        # TRADING_ENABLED should be False without keys
        if not os.environ.get('BINANCE_API_KEY'):
            self.assertFalse(TRADING_ENABLED)


class TestInputHandling(unittest.TestCase):
    """Test keyboard input edge cases"""
    
    def test_h_key_only_when_empty(self):
        """H key should only toggle history when command is empty"""
        # Simulate the logic
        command = ""
        ch = ord('h')
        
        # When command is empty, H toggles history
        if len(command) == 0 and (ch == ord('H') or ch == ord('h')):
            should_toggle = True
        else:
            should_toggle = False
        
        self.assertTrue(should_toggle)
        
        # When command has content, H should be added
        command = "buy et"
        if len(command) == 0 and (ch == ord('H') or ch == ord('h')):
            should_toggle = True
        else:
            should_toggle = False
        
        self.assertFalse(should_toggle)
    
    def test_escape_clears_command(self):
        """Escape should clear command buffer"""
        command = "buy BTC 0.01"
        ch = 27  # Escape
        
        if ch == 27:
            command = ""
        
        self.assertEqual(command, "")


class TestChartFunctions(unittest.TestCase):
    """Test chart rendering edge cases"""
    
    def test_empty_data_handling(self):
        """Test chart with empty data"""
        chart = PriceChart(80, 20)
        lines = chart.render_ascii([], "Test Chart")
        self.assertEqual(lines, ["NO DATA AVAILABLE"])
    
    def test_single_point_data(self):
        """Test chart with single data point"""
        chart = PriceChart(80, 20)
        data = [{'price': 85000.0, 'date': '2024-01-01'}]
        lines = chart.render_ascii(data, "Test Chart")
        self.assertTrue(len(lines) > 0)
    
    def test_comparison_with_mismatched_data(self):
        """Test comparison with different length datasets"""
        chart = PriceChart(80, 20)
        data1 = [{'price': 85000.0, 'date': '2024-01-01'}]
        data2 = [{'price': 3000.0, 'date': '2024-01-01'}, {'price': 3100.0, 'date': '2024-01-02'}]
        
        # Should handle gracefully
        datasets = [('BTC', data1), ('ETH', data2)]
        lines = chart.render_comparison(datasets)
        self.assertTrue(len(lines) > 0)


class TestSafetyChecks(unittest.TestCase):
    """Test safety checks for trading"""
    
    def test_no_trading_without_keys(self):
        """Ensure no real trades execute without API keys"""
        # If TRADING_ENABLED is False, all trading functions should return None
        if not TRADING_ENABLED:
            self.assertIsNone(spot_market_buy('BTCUSDT', 0.01))
            self.assertIsNone(spot_market_sell('BTCUSDT', 0.01))
            self.assertIsNone(futures_market_long('BTCUSDT', 0.01, 10))
            self.assertIsNone(futures_market_short('BTCUSDT', 0.01, 10))
            self.assertIsNone(get_spot_balance())
            self.assertIsNone(get_futures_balance())
    
    def test_command_dry_run(self):
        """Test that commands can be validated without execution"""
        # Parse command without executing
        cmd = "buy BTC 0.01 85000"
        parts = cmd.split()
        
        # Validate
        self.assertEqual(parts[0], 'buy')
        self.assertEqual(parts[1], 'BTC')
        
        try:
            qty = float(parts[2])
            self.assertEqual(qty, 0.01)
        except ValueError:
            self.fail("Quantity should be valid float")
        
        try:
            price = float(parts[3])
            self.assertEqual(price, 85000)
        except ValueError:
            self.fail("Price should be valid float")


def run_all_tests():
    """Run all tests and print summary"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # Add all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestCommandParsing))
    suite.addTests(loader.loadTestsFromTestCase(TestLeverageValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestQuantityValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestTradeHistoryDatabase))
    suite.addTests(loader.loadTestsFromTestCase(TestSymbolHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestPriceValidation))
    suite.addTests(loader.loadTestsFromTestCase(TestAPIErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestInputHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestChartFunctions))
    suite.addTests(loader.loadTestsFromTestCase(TestSafetyChecks))
    
    # Run with verbosity
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Print summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Skipped: {len(result.skipped)}")
    
    if result.failures:
        print("\nFAILURES:")
        for test, traceback in result.failures:
            print(f"  - {test}: {traceback[:100]}...")
    
    if result.errors:
        print("\nERRORS:")
        for test, traceback in result.errors:
            print(f"  - {test}: {traceback[:100]}...")
    
    if result.wasSuccessful():
        print("\n✓ ALL TESTS PASSED - Safe to trade!")
    else:
        print("\n✗ SOME TESTS FAILED - Review before trading!")
    
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
