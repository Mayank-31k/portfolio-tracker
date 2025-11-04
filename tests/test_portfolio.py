"""
Basic tests for portfolio functionality.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.portfolio.position import Position
from src.portfolio.portfolio import Portfolio
from src.data.price_fetcher import PriceFetcher
import pytest


def test_position_creation():
    """Test creating a position."""
    pos = Position('AAPL', 10, 150.0)

    assert pos.ticker == 'AAPL'
    assert pos.quantity == 10
    assert pos.entry_price == 150.0
    assert pos.cost_basis == 1500.0


def test_position_pnl():
    """Test P&L calculation."""
    pos = Position('AAPL', 10, 150.0)
    pos.update_current_price(160.0)

    assert pos.market_value == 1600.0
    assert pos.unrealized_pnl == 100.0
    assert abs(pos.unrealized_pnl_percent - 6.67) < 0.1


def test_price_fetcher():
    """Test price fetching (requires internet)."""
    fetcher = PriceFetcher()

    # Test with a stable ticker
    price = fetcher.get_current_price('AAPL')

    assert price is not None
    assert price > 0


def test_ticker_validation():
    """Test ticker validation."""
    fetcher = PriceFetcher()

    assert fetcher.validate_ticker('AAPL') == True
    assert fetcher.validate_ticker('INVALID_TICKER_XYZ123') == False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
