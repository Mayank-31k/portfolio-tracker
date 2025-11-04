"""
Position class representing a single holding in the portfolio
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class Position:
    """Represents a single position in the portfolio"""

    ticker: str
    quantity: float
    entry_price: float
    entry_date: datetime
    current_price: Optional[float] = None

    def update_current_price(self, price: float):
        """Update the current market price"""
        self.current_price = price

    @property
    def cost_basis(self) -> float:
        """Calculate the total cost basis (amount invested)"""
        return self.quantity * self.entry_price

    @property
    def current_value(self) -> float:
        """Calculate the current market value"""
        if self.current_price is None:
            return self.cost_basis
        return self.quantity * self.current_price

    @property
    def unrealized_pnl(self) -> float:
        """Calculate unrealized profit/loss"""
        return self.current_value - self.cost_basis

    @property
    def unrealized_pnl_percent(self) -> float:
        """Calculate unrealized P&L as percentage"""
        if self.cost_basis == 0:
            return 0.0
        return (self.unrealized_pnl / self.cost_basis) * 100

    def to_dict(self) -> dict:
        """Convert position to dictionary"""
        return {
            'ticker': self.ticker,
            'quantity': self.quantity,
            'entry_price': self.entry_price,
            'entry_date': self.entry_date.isoformat(),
            'current_price': self.current_price,
            'cost_basis': self.cost_basis,
            'current_value': self.current_value,
            'unrealized_pnl': self.unrealized_pnl,
            'unrealized_pnl_percent': self.unrealized_pnl_percent
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'Position':
        """Create position from dictionary"""
        return cls(
            ticker=data['ticker'],
            quantity=data['quantity'],
            entry_price=data['entry_price'],
            entry_date=datetime.fromisoformat(data['entry_date']),
            current_price=data.get('current_price')
        )
