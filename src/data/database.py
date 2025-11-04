"""
Database module for portfolio persistence using SQLite.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import logging
import os

logger = logging.getLogger(__name__)


class Database:
    """Handles all database operations for the portfolio tracker."""

    def __init__(self, db_path: str = 'data/portfolio.db'):
        """Initialize database connection and create tables if needed."""
        # Ensure the directory exists
        os.makedirs(os.path.dirname(db_path), exist_ok=True)

        self.db_path = db_path
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._create_tables()

    def _create_tables(self):
        """Create necessary database tables."""
        cursor = self.conn.cursor()

        # Positions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                quantity REAL NOT NULL,
                entry_price REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                active INTEGER DEFAULT 1
            )
        ''')

        # Transactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ticker TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                quantity REAL NOT NULL,
                price REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                notes TEXT
            )
        ''')

        # Portfolio snapshots for historical tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS portfolio_snapshots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                snapshot_date TEXT NOT NULL,
                total_value REAL NOT NULL,
                total_cost REAL NOT NULL,
                total_pnl REAL NOT NULL,
                total_pnl_percent REAL NOT NULL
            )
        ''')

        self.conn.commit()
        logger.info("Database tables created successfully")

    def add_position(self, ticker: str, quantity: float, entry_price: float,
                    purchase_date: Optional[str] = None) -> int:
        """
        Add a new position to the portfolio.

        Args:
            ticker: Stock ticker symbol
            quantity: Number of shares
            entry_price: Purchase price per share
            purchase_date: Date of purchase (defaults to now)

        Returns:
            Position ID
        """
        if purchase_date is None:
            purchase_date = datetime.now().isoformat()

        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO positions (ticker, quantity, entry_price, purchase_date)
            VALUES (?, ?, ?, ?)
        ''', (ticker.upper(), quantity, entry_price, purchase_date))

        # Record transaction
        cursor.execute('''
            INSERT INTO transactions (ticker, transaction_type, quantity, price, transaction_date)
            VALUES (?, ?, ?, ?, ?)
        ''', (ticker.upper(), 'BUY', quantity, entry_price, purchase_date))

        self.conn.commit()
        logger.info(f"Added position: {quantity} shares of {ticker} at ${entry_price}")
        return cursor.lastrowid

    def get_all_positions(self) -> List[Dict]:
        """
        Get all active positions.

        Returns:
            List of position dictionaries
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT id, ticker, quantity, entry_price, purchase_date
            FROM positions
            WHERE active = 1
        ''')

        positions = []
        for row in cursor.fetchall():
            positions.append({
                'id': row[0],
                'ticker': row[1],
                'quantity': row[2],
                'entry_price': row[3],
                'purchase_date': row[4]
            })

        return positions

    def update_position(self, position_id: int, quantity: float):
        """Update the quantity of a position."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE positions
            SET quantity = ?
            WHERE id = ?
        ''', (quantity, position_id))
        self.conn.commit()

    def close_position(self, position_id: int):
        """Mark a position as closed."""
        cursor = self.conn.cursor()
        cursor.execute('''
            UPDATE positions
            SET active = 0
            WHERE id = ?
        ''', (position_id,))
        self.conn.commit()

    def add_transaction(self, ticker: str, transaction_type: str, quantity: float,
                       price: float, notes: Optional[str] = None):
        """
        Record a transaction.

        Args:
            ticker: Stock ticker symbol
            transaction_type: 'BUY' or 'SELL'
            quantity: Number of shares
            price: Price per share
            notes: Optional notes
        """
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO transactions (ticker, transaction_type, quantity, price, transaction_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (ticker.upper(), transaction_type, quantity, price, datetime.now().isoformat(), notes))
        self.conn.commit()

    def get_transactions(self, ticker: Optional[str] = None) -> List[Dict]:
        """Get all transactions, optionally filtered by ticker."""
        cursor = self.conn.cursor()

        if ticker:
            cursor.execute('''
                SELECT * FROM transactions
                WHERE ticker = ?
                ORDER BY transaction_date DESC
            ''', (ticker.upper(),))
        else:
            cursor.execute('''
                SELECT * FROM transactions
                ORDER BY transaction_date DESC
            ''')

        transactions = []
        for row in cursor.fetchall():
            transactions.append(dict(row))

        return transactions

    def save_snapshot(self, total_value: float, total_cost: float,
                     total_pnl: float, total_pnl_percent: float):
        """Save a portfolio snapshot for historical tracking."""
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT INTO portfolio_snapshots (snapshot_date, total_value, total_cost, total_pnl, total_pnl_percent)
            VALUES (?, ?, ?, ?, ?)
        ''', (datetime.now().isoformat(), total_value, total_cost, total_pnl, total_pnl_percent))
        self.conn.commit()

    def get_snapshots(self, days: int = 30) -> List[Dict]:
        """Get portfolio snapshots for the last N days."""
        cursor = self.conn.cursor()
        cursor.execute('''
            SELECT * FROM portfolio_snapshots
            ORDER BY snapshot_date DESC
            LIMIT ?
        ''', (days,))

        snapshots = []
        for row in cursor.fetchall():
            snapshots.append(dict(row))

        return snapshots

    def close(self):
        """Close the database connection."""
        self.conn.close()
