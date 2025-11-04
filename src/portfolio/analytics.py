"""
Analytics module for calculating portfolio performance metrics.
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional
from datetime import datetime, timedelta


class PortfolioAnalytics:
    """Calculate various portfolio performance metrics."""

    @staticmethod
    def calculate_daily_returns(portfolio_values: pd.DataFrame) -> pd.Series:
        """
        Calculate daily returns from portfolio values.

        Args:
            portfolio_values: DataFrame with 'date' and 'value' columns

        Returns:
            Series of daily returns
        """
        if len(portfolio_values) < 2:
            return pd.Series([])

        returns = portfolio_values['value'].pct_change().dropna()
        return returns

    @staticmethod
    def calculate_total_return(initial_value: float, current_value: float) -> float:
        """
        Calculate total return percentage.

        Args:
            initial_value: Initial portfolio value
            current_value: Current portfolio value

        Returns:
            Total return as percentage
        """
        if initial_value == 0:
            return 0
        return ((current_value - initial_value) / initial_value) * 100

    @staticmethod
    def calculate_volatility(returns: pd.Series, annualize: bool = True) -> float:
        """
        Calculate portfolio volatility (standard deviation of returns).

        Args:
            returns: Series of daily returns
            annualize: Whether to annualize the volatility

        Returns:
            Volatility as decimal
        """
        if len(returns) < 2:
            return 0

        vol = returns.std()

        if annualize:
            # Assuming 252 trading days per year
            vol = vol * np.sqrt(252)

        return vol

    @staticmethod
    def calculate_sharpe_ratio(returns: pd.Series, risk_free_rate: float = 0.02) -> float:
        """
        Calculate Sharpe ratio (risk-adjusted return).

        Args:
            returns: Series of daily returns
            risk_free_rate: Annual risk-free rate (default 2%)

        Returns:
            Sharpe ratio
        """
        if len(returns) < 2:
            return 0

        # Convert annual risk-free rate to daily
        daily_rf = risk_free_rate / 252

        excess_returns = returns - daily_rf
        avg_excess_return = excess_returns.mean()
        std_returns = returns.std()

        if std_returns == 0:
            return 0

        # Annualize
        sharpe = (avg_excess_return / std_returns) * np.sqrt(252)
        return sharpe

    @staticmethod
    def calculate_max_drawdown(portfolio_values: pd.DataFrame) -> Dict[str, float]:
        """
        Calculate maximum drawdown.

        Args:
            portfolio_values: DataFrame with 'date' and 'value' columns

        Returns:
            Dictionary with max drawdown percentage and value
        """
        if len(portfolio_values) < 2:
            return {'max_drawdown_pct': 0, 'max_drawdown_value': 0}

        values = portfolio_values['value']
        cummax = values.cummax()
        drawdown = (values - cummax) / cummax

        max_dd_pct = drawdown.min() * 100
        max_dd_value = (values - cummax).min()

        return {
            'max_drawdown_pct': max_dd_pct,
            'max_drawdown_value': max_dd_value
        }

    @staticmethod
    def calculate_win_rate(positions: List[Dict]) -> float:
        """
        Calculate win rate (percentage of profitable positions).

        Args:
            positions: List of position dictionaries

        Returns:
            Win rate as percentage
        """
        if not positions:
            return 0

        profitable = sum(1 for pos in positions if pos.get('unrealized_pnl', 0) > 0)
        return (profitable / len(positions)) * 100

    @staticmethod
    def get_performance_summary(portfolio_values: pd.DataFrame,
                                positions: List[Dict]) -> Dict:
        """
        Get comprehensive performance summary.

        Args:
            portfolio_values: DataFrame with portfolio history
            positions: List of current positions

        Returns:
            Dictionary with various performance metrics
        """
        if len(portfolio_values) < 2:
            return {
                'total_return': 0,
                'volatility': 0,
                'sharpe_ratio': 0,
                'max_drawdown_pct': 0,
                'win_rate': 0,
                'avg_return': 0
            }

        returns = PortfolioAnalytics.calculate_daily_returns(portfolio_values)

        initial_value = portfolio_values['value'].iloc[0]
        current_value = portfolio_values['value'].iloc[-1]

        total_return = PortfolioAnalytics.calculate_total_return(initial_value, current_value)
        volatility = PortfolioAnalytics.calculate_volatility(returns)
        sharpe_ratio = PortfolioAnalytics.calculate_sharpe_ratio(returns)
        max_drawdown = PortfolioAnalytics.calculate_max_drawdown(portfolio_values)
        win_rate = PortfolioAnalytics.calculate_win_rate(positions)

        return {
            'total_return': total_return,
            'volatility': volatility * 100,  # Convert to percentage
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown_pct': max_drawdown['max_drawdown_pct'],
            'win_rate': win_rate,
            'avg_return': returns.mean() * 100 if len(returns) > 0 else 0
        }
