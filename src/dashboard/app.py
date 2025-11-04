"""
Streamlit dashboard for portfolio tracking and visualization.
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.portfolio.portfolio import Portfolio
from src.portfolio.analytics import PortfolioAnalytics

# Page configuration
st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
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


@st.cache_resource
def get_portfolio():
    """Initialize portfolio (cached)."""
    return Portfolio()


def format_currency(value):
    """Format value as currency."""
    return f"${value:,.2f}"


def format_percent(value):
    """Format value as percentage."""
    return f"{value:.2f}%"


def main():
    st.title("📈 Portfolio Tracker")
    st.markdown("---")

    # Initialize portfolio
    portfolio = get_portfolio()

    # Sidebar - Add Position
    with st.sidebar:
        st.header("Add New Position")

        with st.form("add_position_form"):
            ticker = st.text_input("Ticker Symbol", placeholder="e.g., AAPL").upper()
            quantity = st.number_input("Quantity", min_value=0.0, step=0.1, value=1.0)
            entry_price = st.number_input("Entry Price ($)", min_value=0.0, step=0.01, value=100.0)

            submitted = st.form_submit_button("Add Position")

            if submitted:
                if ticker:
                    try:
                        portfolio.add_position(ticker, quantity, entry_price)
                        st.success(f"Added {quantity} shares of {ticker} at {format_currency(entry_price)}")
                        st.rerun()
                    except ValueError as e:
                        st.error(str(e))
                else:
                    st.error("Please enter a ticker symbol")

        st.markdown("---")

        # Refresh prices button
        if st.button("🔄 Refresh Prices", use_container_width=True):
            with st.spinner("Updating prices..."):
                portfolio.update_all_prices()
                st.success("Prices updated!")
                st.rerun()

    # Update prices
    portfolio.update_all_prices()

    # Check if portfolio is empty
    if not portfolio.positions:
        st.info("👈 Add your first position using the sidebar to get started!")
        st.markdown("""
        ### Welcome to Portfolio Tracker!

        This app helps you:
        - Track your stock positions in real-time
        - Monitor profit & loss (P&L)
        - Visualize asset allocation
        - Analyze portfolio performance

        **Get started by adding a position in the sidebar.**
        """)
        return

    # Portfolio Summary
    summary = portfolio.get_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Value",
            value=format_currency(summary['total_market_value']),
            delta=format_currency(summary['total_unrealized_pnl'])
        )

    with col2:
        st.metric(
            label="Total Cost",
            value=format_currency(summary['total_cost_basis'])
        )

    with col3:
        pnl_color = "normal" if summary['total_unrealized_pnl'] >= 0 else "inverse"
        st.metric(
            label="Unrealized P&L",
            value=format_currency(summary['total_unrealized_pnl']),
            delta=format_percent(summary['total_unrealized_pnl_percent']),
            delta_color=pnl_color
        )

    with col4:
        st.metric(
            label="Positions",
            value=summary['total_positions']
        )

    st.markdown("---")

    # Positions Table
    st.subheader("📊 Current Positions")

    positions_data = portfolio.get_positions_data()
    if positions_data:
        df = pd.DataFrame(positions_data)

        # Format the display
        display_df = pd.DataFrame({
            'Ticker': df['ticker'],
            'Quantity': df['quantity'],
            'Entry Price': df['entry_price'].apply(format_currency),
            'Current Price': df['current_price'].apply(lambda x: format_currency(x) if x else 'N/A'),
            'Market Value': df['market_value'].apply(lambda x: format_currency(x) if x else 'N/A'),
            'Cost Basis': df['cost_basis'].apply(format_currency),
            'P&L ($)': df['unrealized_pnl'].apply(lambda x: format_currency(x) if x is not None else 'N/A'),
            'P&L (%)': df['unrealized_pnl_percent'].apply(lambda x: format_percent(x) if x is not None else 'N/A')
        })

        st.dataframe(display_df, use_container_width=True, hide_index=True)

        # Remove position section
        st.markdown("---")
        st.subheader("Remove Position")
        col1, col2 = st.columns([3, 1])
        with col1:
            ticker_to_remove = st.selectbox(
                "Select position to remove",
                options=[pos['ticker'] for pos in positions_data],
                key="remove_ticker"
            )
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Remove", type="secondary"):
                portfolio.remove_position(ticker_to_remove)
                st.success(f"Removed {ticker_to_remove}")
                st.rerun()

    st.markdown("---")

    # Visualizations
    col1, col2 = st.columns(2)

    with col1:
        # Asset Allocation Pie Chart
        st.subheader("🥧 Asset Allocation")

        if summary['allocation']:
            allocation_df = pd.DataFrame([
                {'Ticker': ticker, 'Allocation': alloc}
                for ticker, alloc in summary['allocation'].items()
            ])

            fig = px.pie(
                allocation_df,
                values='Allocation',
                names='Ticker',
                title='Portfolio Allocation by Asset',
                hole=0.4
            )
            fig.update_traces(textposition='inside', textinfo='percent+label')
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        # P&L Bar Chart
        st.subheader("💰 P&L by Position")

        if positions_data:
            pnl_df = pd.DataFrame([
                {
                    'Ticker': pos['ticker'],
                    'P&L': pos['unrealized_pnl'] if pos['unrealized_pnl'] is not None else 0
                }
                for pos in positions_data
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

    # Portfolio Performance Metrics
    st.markdown("---")
    st.subheader("📈 Performance Metrics")

    # Get historical snapshots
    snapshots = portfolio.db.get_snapshots(30)

    if snapshots and len(snapshots) > 1:
        snapshots_df = pd.DataFrame(snapshots)
        snapshots_df['snapshot_date'] = pd.to_datetime(snapshots_df['snapshot_date'])
        snapshots_df = snapshots_df.sort_values('snapshot_date')

        # Performance chart
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=snapshots_df['snapshot_date'],
            y=snapshots_df['total_value'],
            mode='lines+markers',
            name='Portfolio Value',
            line=dict(color='blue', width=2),
            fill='tonexty'
        ))

        fig.update_layout(
            title='Portfolio Value Over Time',
            xaxis_title='Date',
            yaxis_title='Value ($)',
            hovermode='x unified'
        )

        st.plotly_chart(fig, use_container_width=True)

        # Calculate analytics
        analytics_df = snapshots_df.rename(columns={'total_value': 'value', 'snapshot_date': 'date'})
        performance = PortfolioAnalytics.get_performance_summary(analytics_df, positions_data)

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Total Return", format_percent(performance['total_return']))
            st.metric("Volatility", format_percent(performance['volatility']))

        with col2:
            st.metric("Sharpe Ratio", f"{performance['sharpe_ratio']:.2f}")
            st.metric("Win Rate", format_percent(performance['win_rate']))

        with col3:
            st.metric("Max Drawdown", format_percent(performance['max_drawdown_pct']))
            st.metric("Avg Daily Return", format_percent(performance['avg_return']))

    else:
        st.info("Portfolio history data is limited. Performance metrics will be available after more snapshots are collected.")

    # Save snapshot button
    if st.button("💾 Save Portfolio Snapshot"):
        portfolio.save_snapshot()
        st.success("Portfolio snapshot saved!")
        st.rerun()

    # Footer
    st.markdown("---")
    st.markdown("""
        <div style='text-align: center; color: gray;'>
            <p>Portfolio Tracker MVP | Built with Streamlit & yfinance</p>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
