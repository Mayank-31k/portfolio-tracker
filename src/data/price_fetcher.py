"""
Price fetcher module for retrieving real-time and historical market data.
Uses yfinance as the primary data source.
"""

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PriceFetcher:
    """Fetches real-time and historical price data for various assets."""

    def __init__(self):
        self.cache = {}
        self.cache_duration = timedelta(minutes=1)  # Cache prices for 1 minute

    def get_current_price(self, ticker: str) -> Optional[float]:
        """
        Fetch the current price for a given ticker.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'GOOGL')

        Returns:
            Current price as float, or None if error
        """
        try:
            # Check cache first
            cache_key = f"{ticker}_price"
            if cache_key in self.cache:
                price, timestamp = self.cache[cache_key]
                if datetime.now() - timestamp < self.cache_duration:
                    return price

            # Fetch fresh data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')

            if hist.empty:
                logger.error(f"No data found for ticker: {ticker}")
                return None

            current_price = hist['Close'].iloc[-1]

            # Update cache
            self.cache[cache_key] = (current_price, datetime.now())

            return float(current_price)

        except Exception as e:
            logger.error(f"Error fetching price for {ticker}: {str(e)}")
            return None

    def get_multiple_prices(self, tickers: List[str]) -> Dict[str, Optional[float]]:
        """
        Fetch current prices for multiple tickers efficiently.

        Args:
            tickers: List of ticker symbols

        Returns:
            Dictionary mapping ticker to current price
        """
        prices = {}
        for ticker in tickers:
            prices[ticker] = self.get_current_price(ticker)
        return prices

    def get_historical_data(self, ticker: str, period: str = '1mo') -> Optional[pd.DataFrame]:
        """
        Fetch historical price data for a ticker.

        Args:
            ticker: Stock ticker symbol
            period: Time period (e.g., '1d', '5d', '1mo', '3mo', '1y', '5y')

        Returns:
            DataFrame with historical OHLCV data
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period=period)

            if hist.empty:
                logger.error(f"No historical data found for ticker: {ticker}")
                return None

            return hist

        except Exception as e:
            logger.error(f"Error fetching historical data for {ticker}: {str(e)}")
            return None

    def get_ticker_info(self, ticker: str) -> Optional[Dict]:
        """
        Get detailed information about a ticker.

        Args:
            ticker: Stock ticker symbol

        Returns:
            Dictionary with ticker information
        """
        try:
            stock = yf.Ticker(ticker)
            info = stock.info

            return {
                'name': info.get('longName', ticker),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'currency': info.get('currency', 'USD'),
                'exchange': info.get('exchange', 'N/A')
            }

        except Exception as e:
            logger.error(f"Error fetching info for {ticker}: {str(e)}")
            return None

    def validate_ticker(self, ticker: str) -> bool:
        """
        Validate if a ticker symbol is valid.

        Args:
            ticker: Stock ticker symbol

        Returns:
            True if valid, False otherwise
        """
        try:
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d')
            return not hist.empty
        except:
            return False
