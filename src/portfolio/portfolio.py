"""
Portfolio management module
"""
from typing import List, Dict, Optional
from datetime import datetime
from .position import Position
from ..data.price_fetcher import PriceFetcher


class Portfolio:
    """Manages a collection of positions"""

    def __init__(self):
        self.positions: List[Position] = []
        self.price_fetcher = PriceFetcher()

    def add_position(self, ticker: str, quantity: float, entry_price: float,
                    entry_date: Optional[datetime] = None) -> Position:
        """
        Add a new position to the portfolio

        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            entry_price: Price per share at entry
            entry_date: Date of entry (defaults to now)

        Returns:
            The created Position object
        """
        if entry_date is None:
            entry_date = datetime.now()

        # Check if position already exists
        existing_pos = self.get_position(ticker)
        if existing_pos:
            # Average down the position
            total_quantity = existing_pos.quantity + quantity
            total_cost = (existing_pos.quantity * existing_pos.entry_price +
                         quantity * entry_price)
            existing_pos.quantity = total_quantity
            existing_pos.entry_price = total_cost / total_quantity
            return existing_pos
        else:
            position = Position(
                ticker=ticker,
                quantity=quantity,
                entry_price=entry_price,
                entry_date=entry_date
            )
            self.positions.append(position)
            return position

    def remove_position(self, ticker: str, quantity: Optional[float] = None):
        """
        Remove a position or reduce its quantity

        Args:
            ticker: Stock ticker symbol
            quantity: Quantity to remove (if None, removes entire position)
        """
        position = self.get_position(ticker)
        if not position:
            raise ValueError(f"Position {ticker} not found")

        if quantity is None or quantity >= position.quantity:
            self.positions.remove(position)
        else:
            position.quantity -= quantity

    def get_position(self, ticker: str) -> Optional[Position]:
        """Get a position by ticker symbol"""
        for position in self.positions:
            if position.ticker.upper() == ticker.upper():
                return position
        return None

    def update_prices(self):
        """Update current prices for all positions"""
        if not self.positions:
            return

        tickers = [pos.ticker for pos in self.positions]
        prices = self.price_fetcher.get_multiple_prices(tickers)

        for position in self.positions:
            if position.ticker in prices:
                position.update_current_price(prices[position.ticker])

    @property
    def total_value(self) -> float:
        """Calculate total portfolio value"""
        return sum(pos.current_value for pos in self.positions)

    @property
    def total_cost_basis(self) -> float:
        """Calculate total cost basis"""
        return sum(pos.cost_basis for pos in self.positions)

    @property
    def total_pnl(self) -> float:
        """Calculate total unrealized P&L"""
        return self.total_value - self.total_cost_basis

    @property
    def total_pnl_percent(self) -> float:
        """Calculate total P&L as percentage"""
        if self.total_cost_basis == 0:
            return 0.0
        return (self.total_pnl / self.total_cost_basis) * 100

    def get_asset_allocation(self) -> Dict[str, float]:
        """
        Get asset allocation as percentage of portfolio

        Returns:
            Dictionary mapping ticker to percentage of portfolio
        """
        if self.total_value == 0:
            return {}

        return {
            pos.ticker: (pos.current_value / self.total_value) * 100
            for pos in self.positions
        }

    def get_summary(self) -> dict:
        """Get portfolio summary statistics"""
        return {
            'total_value': self.total_value,
            'total_cost_basis': self.total_cost_basis,
            'total_pnl': self.total_pnl,
            'total_pnl_percent': self.total_pnl_percent,
            'num_positions': len(self.positions),
            'asset_allocation': self.get_asset_allocation()
        }

    def to_dict(self) -> dict:
        """Convert portfolio to dictionary"""
        return {
            'positions': [pos.to_dict() for pos in self.positions],
            'summary': self.get_summary()
        }
