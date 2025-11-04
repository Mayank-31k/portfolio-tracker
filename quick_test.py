#!/usr/bin/env python3
"""
Quick test script to verify portfolio tracker setup.
"""

import sys
import os

# Add src to path
sys.path.append(os.path.dirname(__file__))

from src.portfolio.position import Position
from src.portfolio.analytics import PortfolioAnalytics
import pandas as pd

def test_basic_functionality():
    """Test basic portfolio functionality."""
    print("🧪 Testing Portfolio Tracker Components\n")

    # Test 1: Position creation
    print("1️⃣  Testing Position creation...")
    pos = Position('AAPL', 10, 150.0)
    assert pos.ticker == 'AAPL'
    assert pos.cost_basis == 1500.0
    print("   ✅ Position created successfully")
    print(f"      {pos}")

    # Test 2: P&L calculation
    print("\n2️⃣  Testing P&L calculation...")
    pos.update_current_price(165.0)
    assert pos.market_value == 1650.0
    assert pos.unrealized_pnl == 150.0
    print("   ✅ P&L calculated correctly")
    print(f"      Market Value: ${pos.market_value:.2f}")
    print(f"      Unrealized P&L: ${pos.unrealized_pnl:.2f} ({pos.unrealized_pnl_percent:.2f}%)")

    # Test 3: Analytics
    print("\n3️⃣  Testing Analytics...")
    test_data = pd.DataFrame({
        'date': pd.date_range('2024-01-01', periods=10),
        'value': [1000, 1020, 1015, 1030, 1025, 1040, 1050, 1045, 1060, 1070]
    })

    total_return = PortfolioAnalytics.calculate_total_return(
        test_data['value'].iloc[0],
        test_data['value'].iloc[-1]
    )
    print("   ✅ Analytics working")
    print(f"      Total Return: {total_return:.2f}%")

    print("\n✨ All tests passed! Portfolio Tracker is ready to use.\n")
    print("📚 Next steps:")
    print("   1. Install dependencies: pip install -r requirements.txt")
    print("   2. Run the dashboard: streamlit run src/dashboard/app.py")
    print("   3. Or use the run script: ./run.sh\n")

if __name__ == "__main__":
    try:
        test_basic_functionality()
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        sys.exit(1)
