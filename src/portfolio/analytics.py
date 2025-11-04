"""
Advanced analytics module for portfolio metrics
"""
import numpy as np
import pandas as pd
from typing import List, Tuple
from datetime import datetime, timedelta
from ..data.price_fetcher import PriceFetcher


class PortfolioAnalytics:
    """Calculate advanced portfolio metrics"""

    def __init__(self):
        self.price_fetcher = PriceFetcher()

    def calculate_sharpe_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted return)

        Args:
            returns: Series of daily returns
            risk_free_rate: Annual risk-free rate (default 2%)

        Returns:
            Sharpe ratio
        """
        if len(returns) == 0 or returns.std() == 0:
            return 0.0

        # Convert annual risk-free rate to daily
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1

        # Calculate excess returns
        excess_returns = returns - daily_rf

        # Sharpe ratio = mean(excess returns) / std(returns) * sqrt(252) for annualization
        sharpe = (excess_returns.mean() / returns.std()) * np.sqrt(252)
        return float(sharpe)

    def calculate_volatility(self, returns: pd.Series, annualized: bool = True) -> float:
        """
        Calculate portfolio volatility (standard deviation)

        Args:
            returns: Series of daily returns
            annualized: If True, annualize the volatility

        Returns:
            Volatility
        """
        if len(returns) == 0:
            return 0.0

        vol = returns.std()

        if annualized:
            vol *= np.sqrt(252)  # Annualize

        return float(vol)

    def calculate_max_drawdown(self, values: pd.Series) -> Tuple[float, float]:
        """
        Calculate maximum drawdown

        Args:
            values: Series of portfolio values over time

        Returns:
            Tuple of (max_drawdown percentage, max_drawdown value)
        """
        if len(values) == 0:
            return 0.0, 0.0

        # Calculate running maximum
        running_max = values.expanding().max()

        # Calculate drawdown
        drawdown = (values - running_max) / running_max

        max_dd_pct = drawdown.min() * 100
        max_dd_value = (values - running_max).min()

        return float(max_dd_pct), float(max_dd_value)

    def calculate_returns(self, values: pd.Series) -> pd.Series:
        """
        Calculate daily returns

        Args:
            values: Series of portfolio values

        Returns:
            Series of daily returns
        """
        if len(values) == 0:
            return pd.Series([])

        returns = values.pct_change().dropna()
        return returns

    def calculate_beta(self, portfolio_returns: pd.Series, market_returns: pd.Series) -> float:
        """
        Calculate portfolio beta (correlation to market)

        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Series of market benchmark returns

        Returns:
            Beta value
        """
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 0.0

        # Align the series
        aligned_data = pd.DataFrame({
            'portfolio': portfolio_returns,
            'market': market_returns
        }).dropna()

        if len(aligned_data) < 2:
            return 0.0

        # Calculate covariance and variance
        covariance = aligned_data['portfolio'].cov(aligned_data['market'])
        market_variance = aligned_data['market'].var()

        if market_variance == 0:
            return 0.0

        beta = covariance / market_variance
        return float(beta)

    def calculate_alpha(self, portfolio_returns: pd.Series, market_returns: pd.Series,
                       risk_free_rate: float = 0.02) -> float:
        """
        Calculate portfolio alpha (excess return over expected return)

        Args:
            portfolio_returns: Series of portfolio returns
            market_returns: Series of market benchmark returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Alpha value (annualized percentage)
        """
        if len(portfolio_returns) == 0 or len(market_returns) == 0:
            return 0.0

        beta = self.calculate_beta(portfolio_returns, market_returns)

        # Convert to daily risk-free rate
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1

        # Calculate average returns
        avg_portfolio_return = portfolio_returns.mean()
        avg_market_return = market_returns.mean()

        # Alpha = Portfolio return - (Risk-free rate + Beta * (Market return - Risk-free rate))
        alpha = avg_portfolio_return - (daily_rf + beta * (avg_market_return - daily_rf))

        # Annualize
        alpha_annual = alpha * 252 * 100

        return float(alpha_annual)

    def get_benchmark_returns(self, ticker: str = "SPY", period: str = "1mo") -> pd.Series:
        """
        Get benchmark returns (default S&P 500)

        Args:
            ticker: Benchmark ticker (default SPY)
            period: Time period

        Returns:
            Series of benchmark returns
        """
        data = self.price_fetcher.get_historical_data(ticker, period)

        if data.empty:
            return pd.Series([])

        returns = data['Close'].pct_change().dropna()
        return returns

    def calculate_correlation_matrix(self, tickers: List[str], period: str = "3mo") -> pd.DataFrame:
        """
        Calculate correlation matrix between holdings

        Args:
            tickers: List of ticker symbols
            period: Time period for analysis

        Returns:
            Correlation matrix
        """
        if len(tickers) == 0:
            return pd.DataFrame()

        # Fetch historical data for all tickers
        price_data = {}
        for ticker in tickers:
            data = self.price_fetcher.get_historical_data(ticker, period)
            if not data.empty:
                price_data[ticker] = data['Close']

        if len(price_data) == 0:
            return pd.DataFrame()

        # Create DataFrame of prices
        prices_df = pd.DataFrame(price_data)

        # Calculate returns
        returns_df = prices_df.pct_change().dropna()

        # Calculate correlation matrix
        corr_matrix = returns_df.corr()

        return corr_matrix

    def calculate_var(self, returns: pd.Series, confidence_level: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR)

        Args:
            returns: Series of returns
            confidence_level: Confidence level (default 95%)

        Returns:
            VaR value as percentage
        """
        if len(returns) == 0:
            return 0.0

        var = np.percentile(returns, (1 - confidence_level) * 100)
        return float(var * 100)

    def calculate_sortino_ratio(self, returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sortino ratio (like Sharpe but only considers downside volatility)

        Args:
            returns: Series of returns
            risk_free_rate: Annual risk-free rate

        Returns:
            Sortino ratio
        """
        if len(returns) == 0:
            return 0.0

        # Convert to daily risk-free rate
        daily_rf = (1 + risk_free_rate) ** (1/252) - 1

        # Calculate excess returns
        excess_returns = returns - daily_rf

        # Calculate downside deviation (only negative returns)
        downside_returns = excess_returns[excess_returns < 0]

        if len(downside_returns) == 0 or downside_returns.std() == 0:
            return 0.0

        sortino = (excess_returns.mean() / downside_returns.std()) * np.sqrt(252)
        return float(sortino)
