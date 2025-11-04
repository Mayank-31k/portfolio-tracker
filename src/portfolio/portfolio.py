"""
Portfolio management module for tracking and managing multiple positions.
"""

from typing import List, Dict, Optional
import logging
from src.portfolio.position import Position
from src.data.price_fetcher import PriceFetcher
from src.data.database import Database

logger = logging.getLogger(__name__)


class Portfolio:
    """Manages a collection of positions and portfolio-level operations."""

    def __init__(self, db_path: str = 'data/portfolio.db'):
        """
        Initialize portfolio.

        Args:
            db_path: Path to SQLite database
        """
        self.db = Database(db_path)
        self.price_fetcher = PriceFetcher()
        self.positions: List[Position] = []
        self.load_positions()

    def load_positions(self):
        """Load all active positions from database."""
        db_positions = self.db.get_all_positions()
        self.positions = []

        for pos_data in db_positions:
            position = Position(
                ticker=pos_data['ticker'],
                quantity=pos_data['quantity'],
                entry_price=pos_data['entry_price'],
                purchase_date=pos_data['purchase_date'],
                position_id=pos_data['id']
            )
            self.positions.append(position)

        logger.info(f"Loaded {len(self.positions)} positions from database")

    def add_position(self, ticker: str, quantity: float, entry_price: float) -> Position:
        """
        Add a new position to the portfolio.

        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            entry_price: Purchase price per share

        Returns:
            Created Position object
        """
        # Validate ticker
        if not self.price_fetcher.validate_ticker(ticker):
            raise ValueError(f"Invalid ticker symbol: {ticker}")

        # Save to database
        position_id = self.db.add_position(ticker, quantity, entry_price)

        # Create position object
        position = Position(ticker, quantity, entry_price, position_id=position_id)
        self.positions.append(position)

        logger.info(f"Added position: {position}")
        return position

    def remove_position(self, ticker: str):
        """
        Remove a position from the portfolio.

        Args:
            ticker: Stock ticker symbol to remove
        """
        position = self.get_position(ticker)
        if position:
            self.db.close_position(position.id)
            self.positions.remove(position)
            logger.info(f"Removed position: {ticker}")
        else:
            logger.warning(f"Position not found: {ticker}")

    def get_position(self, ticker: str) -> Optional[Position]:
        """Get a position by ticker symbol."""
        for position in self.positions:
            if position.ticker == ticker.upper():
                return position
        return None

    def update_all_prices(self):
        """Update current prices for all positions."""
        if not self.positions:
            return

        tickers = [pos.ticker for pos in self.positions]
        prices = self.price_fetcher.get_multiple_prices(tickers)

        for position in self.positions:
            price = prices.get(position.ticker)
            if price is not None:
                position.update_current_price(price)
            else:
                logger.warning(f"Could not fetch price for {position.ticker}")

    @property
    def total_cost_basis(self) -> float:
        """Calculate total cost basis of all positions."""
        return sum(pos.cost_basis for pos in self.positions)

    @property
    def total_market_value(self) -> float:
        """Calculate total current market value."""
        total = 0
        for pos in self.positions:
            if pos.market_value is not None:
                total += pos.market_value
        return total

    @property
    def total_unrealized_pnl(self) -> float:
        """Calculate total unrealized P&L in dollars."""
        return self.total_market_value - self.total_cost_basis

    @property
    def total_unrealized_pnl_percent(self) -> float:
        """Calculate total unrealized P&L as percentage."""
        if self.total_cost_basis == 0:
            return 0
        return (self.total_unrealized_pnl / self.total_cost_basis) * 100

    def get_allocation(self) -> Dict[str, float]:
        """
        Get asset allocation as percentages.

        Returns:
            Dictionary mapping ticker to allocation percentage
        """
        if self.total_market_value == 0:
            return {}

        allocation = {}
        for position in self.positions:
            if position.market_value is not None:
                allocation[position.ticker] = (position.market_value / self.total_market_value) * 100

        return allocation

    def get_summary(self) -> Dict:
        """
        Get portfolio summary statistics.

        Returns:
            Dictionary with portfolio metrics
        """
        return {
            'total_positions': len(self.positions),
            'total_cost_basis': self.total_cost_basis,
            'total_market_value': self.total_market_value,
            'total_unrealized_pnl': self.total_unrealized_pnl,
            'total_unrealized_pnl_percent': self.total_unrealized_pnl_percent,
            'allocation': self.get_allocation()
        }

    def get_positions_data(self) -> List[Dict]:
        """Get all positions as list of dictionaries."""
        return [pos.to_dict() for pos in self.positions]

    def save_snapshot(self):
        """Save current portfolio state as a snapshot."""
        self.db.save_snapshot(
            total_value=self.total_market_value,
            total_cost=self.total_cost_basis,
            total_pnl=self.total_unrealized_pnl,
            total_pnl_percent=self.total_unrealized_pnl_percent
        )
        logger.info("Portfolio snapshot saved")

    def close(self):
        """Close database connection."""
        self.db.close()
