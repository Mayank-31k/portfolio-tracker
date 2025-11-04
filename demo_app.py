"""
Demo version of Portfolio Tracker with sample data.
Run this to preview the dashboard without needing real market data.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import random

# Page configuration
st.set_page_config(
    page_title="Portfolio Tracker - DEMO",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .metric-card {
        background-color: #f0f2f6;
        padding: 20px;
        border-radius: 10px;
        margin: 10px 0;
    }
    .profit {
        color: #00cc00;
    }
    .loss {
        color: #ff0000;
    }
    </style>
""", unsafe_allow_html=True)

# Sample portfolio data
if 'positions' not in st.session_state:
    st.session_state.positions = [
        {
            'ticker': 'AAPL',
            'quantity': 10,
            'entry_price': 150.0,
            'current_price': 175.50,
            'cost_basis': 1500.0,
            'market_value': 1755.0,
            'unrealized_pnl': 255.0,
            'unrealized_pnl_percent': 17.0
        },
        {
            'ticker': 'GOOGL',
            'quantity': 5,
            'entry_price': 2800.0,
            'current_price': 2650.0,
            'cost_basis': 14000.0,
            'market_value': 13250.0,
            'unrealized_pnl': -750.0,
            'unrealized_pnl_percent': -5.36
        },
        {
            'ticker': 'MSFT',
            'quantity': 15,
            'entry_price': 380.0,
            'current_price': 415.25,
            'cost_basis': 5700.0,
            'market_value': 6228.75,
            'unrealized_pnl': 528.75,
            'unrealized_pnl_percent': 9.28
        },
        {
            'ticker': 'TSLA',
            'quantity': 8,
            'entry_price': 220.0,
            'current_price': 245.80,
            'cost_basis': 1760.0,
            'market_value': 1966.4,
            'unrealized_pnl': 206.4,
            'unrealized_pnl_percent': 11.73
        }
    ]

def format_currency(value):
    """Format value as currency."""
    return f"${value:,.2f}"

def format_percent(value):
    """Format value as percentage."""
    return f"{value:.2f}%"

def main():
    st.title("📈 Portfolio Tracker - DEMO MODE")
    st.info("🎮 This is a demo with sample data. The full version uses real-time market data from yfinance.")
    st.markdown("---")

    # Sidebar
    with st.sidebar:
        st.header("Demo Controls")
        st.markdown("In the full version, you can:")
        st.markdown("- ✅ Add real positions")
        st.markdown("- ✅ Get live price updates")
        st.markdown("- ✅ Track historical performance")
        st.markdown("- ✅ Save portfolio snapshots")

        st.markdown("---")
        st.subheader("Sample Portfolio")
        st.write("Showing 4 positions:")
        for pos in st.session_state.positions:
            st.write(f"• {pos['ticker']}: {pos['quantity']} shares")

        st.markdown("---")
        if st.button("🔄 Simulate Price Update"):
            # Simulate price changes
            for pos in st.session_state.positions:
                change = random.uniform(-0.05, 0.05)  # ±5%
                pos['current_price'] *= (1 + change)
                pos['market_value'] = pos['quantity'] * pos['current_price']
                pos['unrealized_pnl'] = pos['market_value'] - pos['cost_basis']
                pos['unrealized_pnl_percent'] = (pos['unrealized_pnl'] / pos['cost_basis']) * 100
            st.rerun()

    # Calculate totals
    total_cost = sum(pos['cost_basis'] for pos in st.session_state.positions)
    total_value = sum(pos['market_value'] for pos in st.session_state.positions)
    total_pnl = total_value - total_cost
    total_pnl_pct = (total_pnl / total_cost) * 100 if total_cost > 0 else 0

    # Portfolio Summary
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Value",
            value=format_currency(total_value),
            delta=format_currency(total_pnl)
        )

    with col2:
        st.metric(
            label="Total Cost",
            value=format_currency(total_cost)
        )

    with col3:
        pnl_color = "normal" if total_pnl >= 0 else "inverse"
        st.metric(
            label="Unrealized P&L",
            value=format_currency(total_pnl),
            delta=format_percent(total_pnl_pct),
            delta_color=pnl_color
        )

    with col4:
        st.metric(
            label="Positions",
            value=len(st.session_state.positions)
        )

    st.markdown("---")

    # Positions Table
    st.subheader("📊 Current Positions")

    df = pd.DataFrame(st.session_state.positions)
    display_df = pd.DataFrame({
        'Ticker': df['ticker'],
        'Quantity': df['quantity'],
        'Entry Price': df['entry_price'].apply(format_currency),
        'Current Price': df['current_price'].apply(format_currency),
        'Market Value': df['market_value'].apply(format_currency),
        'Cost Basis': df['cost_basis'].apply(format_currency),
        'P&L ($)': df['unrealized_pnl'].apply(format_currency),
        'P&L (%)': df['unrealized_pnl_percent'].apply(format_percent)
    })

    st.dataframe(display_df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Asset Allocation Pie Chart
        st.subheader("🥧 Asset Allocation")

        allocation_df = pd.DataFrame([
            {'Ticker': pos['ticker'], 'Value': pos['market_value']}
            for pos in st.session_state.positions
        ])

        fig = px.pie(
            allocation_df,
            values='Value',
            names='Ticker',
            title='Portfolio Allocation by Asset',
            hole=0.4
        )
        fig.update_traces(textposition='inside', textinfo='percent+label')
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        # P&L Bar Chart
        st.subheader("💰 P&L by Position")

        pnl_df = pd.DataFrame([
            {'Ticker': pos['ticker'], 'P&L': pos['unrealized_pnl']}
            for pos in st.session_state.positions
        ])

        colors = ['green' if x >= 0 else 'red' for x in pnl_df['P&L']]

        fig = go.Figure(data=[
            go.Bar(
                x=pnl_df['Ticker'],
                y=pnl_df['P&L'],
                marker_color=colors,
                text=pnl_df['P&L'].apply(format_currency),
                textposition='outside'
            )
        ])

        fig.update_layout(
            title='Unrealized P&L by Position',
            xaxis_title='Ticker',
            yaxis_title='P&L ($)',
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    # Historical Performance
    st.markdown("---")
    st.subheader("📈 Portfolio Performance Over Time")

    # Generate sample historical data
    dates = pd.date_range(end=datetime.now(), periods=30, freq='D')
    base_value = total_cost
    values = [base_value * (1 + random.uniform(-0.02, 0.03)) for _ in range(30)]

    # Make it somewhat realistic with trending
    for i in range(1, len(values)):
        values[i] = values[i-1] * (1 + random.uniform(-0.02, 0.03))

    history_df = pd.DataFrame({
        'Date': dates,
        'Portfolio Value': values
    })

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=history_df['Date'],
        y=history_df['Portfolio Value'],
        mode='lines+markers',
        name='Portfolio Value',
        line=dict(color='blue', width=2),
        fill='tonexty'
    ))

    fig.update_layout(
        title='Portfolio Value Over Last 30 Days',
        xaxis_title='Date',
        yaxis_title='Value ($)',
        hovermode='x unified'
    )

    st.plotly_chart(fig, use_container_width=True)

    # Performance Metrics
    st.markdown("---")
    st.subheader("📊 Performance Metrics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Return", format_percent(total_pnl_pct))
        st.metric("Volatility (Ann.)", "15.32%")

    with col2:
        st.metric("Sharpe Ratio", "1.42")
        st.metric("Win Rate", "75.00%")

    with col3:
        st.metric("Max Drawdown", "-8.45%")
        st.metric("Avg Daily Return", "0.18%")

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray;'>
            <p>📊 Portfolio Tracker MVP - DEMO MODE</p>
            <p>Built with Streamlit & Plotly | Full version integrates yfinance for real-time data</p>
        </div>
    """, unsafe_allow_html=True)

    st.markdown("---")
    st.info("""
    ### 🚀 To use the full version with real data:

    1. Install all dependencies: `pip install -r requirements.txt`
    2. Run the main app: `streamlit run src/dashboard/app.py`
    3. The full version includes:
       - Real-time price updates from Yahoo Finance
       - Persistent database storage
       - Actual performance calculations
       - Transaction history tracking
    """)

if __name__ == "__main__":
    main()
