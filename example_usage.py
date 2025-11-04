#!/usr/bin/env python3
"""
Example usage of the Portfolio Tracker API.
This demonstrates how to use the portfolio programmatically without the dashboard.
"""

import sys
import os
sys.path.append(os.path.dirname(__file__))

from src.portfolio.portfolio import Portfolio
from src.portfolio.position import Position

def main():
    print("=" * 60)
    print("Portfolio Tracker - Example Usage")
    print("=" * 60)

    # Initialize portfolio
    print("\n1. Initializing portfolio...")
    portfolio = Portfolio(db_path='data/example_portfolio.db')
    print(f"   Loaded {len(portfolio.positions)} existing positions")

    # Add some positions (example - these won't actually be added if they exist)
    print("\n2. Adding positions...")
    try:
        # Note: These will fail if you don't have internet or if ticker is invalid
        # Uncomment to add real positions:
        # portfolio.add_position('AAPL', 10, 150.0)
        # portfolio.add_position('GOOGL', 5, 2800.0)
        # portfolio.add_position('MSFT', 15, 380.0)
        print("   (Skipping - uncomment code to add positions)")
    except Exception as e:
        print(f"   Error: {e}")

    # Update prices
    if portfolio.positions:
        print("\n3. Updating current prices...")
        portfolio.update_all_prices()
        print("   Prices updated!")

        # Display portfolio summary
        print("\n4. Portfolio Summary:")
        print("-" * 60)

        summary = portfolio.get_summary()
        print(f"   Total Positions:     {summary['total_positions']}")
        print(f"   Total Cost Basis:    ${summary['total_cost_basis']:,.2f}")
        print(f"   Total Market Value:  ${summary['total_market_value']:,.2f}")
        print(f"   Unrealized P&L:      ${summary['total_unrealized_pnl']:,.2f}")
        print(f"   P&L Percentage:      {summary['total_unrealized_pnl_percent']:.2f}%")

        # Display individual positions
        print("\n5. Individual Positions:")
        print("-" * 60)

        for pos in portfolio.positions:
            print(f"\n   {pos.ticker}:")
            print(f"      Quantity:        {pos.quantity}")
            print(f"      Entry Price:     ${pos.entry_price:.2f}")
            print(f"      Current Price:   ${pos.current_price:.2f}" if pos.current_price else "      Current Price:   N/A")
            print(f"      Cost Basis:      ${pos.cost_basis:.2f}")
            print(f"      Market Value:    ${pos.market_value:.2f}" if pos.market_value else "      Market Value:    N/A")

            if pos.unrealized_pnl is not None:
                pnl_symbol = "+" if pos.unrealized_pnl >= 0 else ""
                print(f"      Unrealized P&L:  {pnl_symbol}${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_percent:.2f}%)")

        # Display allocation
        print("\n6. Asset Allocation:")
        print("-" * 60)

        allocation = portfolio.get_allocation()
        for ticker, percent in sorted(allocation.items(), key=lambda x: x[1], reverse=True):
            bar_length = int(percent / 2)  # Scale to fit terminal
            bar = "█" * bar_length
            print(f"   {ticker:8} {bar} {percent:.2f}%")

        # Save snapshot
        print("\n7. Saving portfolio snapshot...")
        portfolio.save_snapshot()
        print("   Snapshot saved to database!")

    else:
        print("\n   No positions found!")
        print("   Add positions using the Streamlit dashboard or programmatically.")
        print("\n   Example:")
        print("   portfolio.add_position('AAPL', 10, 150.0)")

    # Close database connection
    portfolio.close()

    print("\n" + "=" * 60)
    print("Done! Run 'streamlit run src/dashboard/app.py' for the dashboard.")
    print("=" * 60 + "\n")

if __name__ == "__main__":
    main()
