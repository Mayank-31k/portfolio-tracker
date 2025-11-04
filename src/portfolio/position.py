"""
Position class representing a single holding in the portfolio.
"""

from datetime import datetime
from typing import Optional


class Position:
    """Represents a single position in the portfolio."""

    def __init__(self, ticker: str, quantity: float, entry_price: float,
                 purchase_date: Optional[str] = None, position_id: Optional[int] = None):
        """
        Initialize a position.

        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            entry_price: Purchase price per share
            purchase_date: Date of purchase
            position_id: Database ID (if loaded from DB)
        """
        self.id = position_id
        self.ticker = ticker.upper()
        self.quantity = quantity
        self.entry_price = entry_price
        self.purchase_date = purchase_date or datetime.now().isoformat()
        self.current_price = None

    def update_current_price(self, price: float):
        """Update the current market price."""
        self.current_price = price

    @property
    def cost_basis(self) -> float:
        """Calculate the total cost basis."""
        return self.quantity * self.entry_price

    @property
    def market_value(self) -> Optional[float]:
        """Calculate current market value."""
        if self.current_price is None:
            return None
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> Optional[float]:
        """Calculate unrealized profit/loss in dollars."""
        if self.market_value is None:
            return None
        return self.market_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self) -> Optional[float]:
        """Calculate unrealized profit/loss as a percentage."""
        if self.unrealized_pnl is None:
            return None
        return (self.unrealized_pnl / self.cost_basis) * 100

    def to_dict(self) -> dict:
        """Convert position to dictionary."""
        return {
            'id': self.id,
            'ticker': self.ticker,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'current_price': self.current_price,
            'cost_basis': self.cost_basis,
            'market_value': self.market_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent,
            'purchase_date': self.purchase_date
        }

    def __repr__(self):
        return f"Position({self.ticker}, qty={self.quantity}, entry=${self.entry_price:.2f})"
