"""
Portfolio Tracker - Streamlit Dashboard
Main application interface for managing and visualizing your investment portfolio
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.portfolio.portfolio import Portfolio
from src.portfolio.position import Position
from src.data.database import Database

# Page configuration
st.set_page_config(
    page_title="Portfolio Tracker",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize database
@st.cache_resource
def get_database():
    return Database()

db = get_database()

# Initialize portfolio in session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = Portfolio()
    # Load positions from database
    positions = db.get_all_positions()
    for pos_data in positions:
        st.session_state.portfolio.add_position(
            ticker=pos_data['ticker'],
            quantity=pos_data['quantity'],
            entry_price=pos_data['entry_price'],
            entry_date=datetime.fromisoformat(pos_data['entry_date'])
        )

portfolio = st.session_state.portfolio

# Title
st.title("📈 Portfolio Tracker")
st.markdown("---")

# Sidebar - Transaction Management
with st.sidebar:
    st.header("Transaction Management")

    transaction_type = st.radio("Transaction Type", ["Buy", "Sell"])

    ticker = st.text_input("Ticker Symbol", placeholder="e.g., AAPL").upper()
    quantity = st.number_input("Quantity", min_value=0.0, value=1.0, step=0.1)
    price = st.number_input("Price per Share ($)", min_value=0.0, value=100.0, step=0.01)

    if transaction_type == "Buy":
        if st.button("🟢 Buy", use_container_width=True):
            if ticker:
                try:
                    portfolio.add_position(ticker, quantity, price)
                    db.add_transaction(ticker, "BUY", quantity, price)

                    # Update or add to database
                    existing_positions = db.get_all_positions()
                    ticker_exists = any(p['ticker'] == ticker for p in existing_positions)

                    if ticker_exists:
                        pos = portfolio.get_position(ticker)
                        db.update_position(ticker, pos.quantity, pos.entry_price)
                    else:
                        db.add_position(ticker, quantity, price, datetime.now())

                    st.success(f"✅ Bought {quantity} shares of {ticker} at ${price}")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a ticker symbol")

    else:  # Sell
        if st.button("🔴 Sell", use_container_width=True):
            if ticker:
                try:
                    pos = portfolio.get_position(ticker)
                    if pos and pos.quantity >= quantity:
                        portfolio.remove_position(ticker, quantity)
                        db.add_transaction(ticker, "SELL", quantity, price)

                        if pos.quantity == quantity:
                            db.remove_position(ticker)
                        else:
                            db.update_position(ticker, pos.quantity, pos.entry_price)

                        st.success(f"✅ Sold {quantity} shares of {ticker} at ${price}")
                        st.rerun()
                    else:
                        st.error(f"Insufficient shares. You have {pos.quantity if pos else 0} shares")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
            else:
                st.warning("Please enter a ticker symbol")

    st.markdown("---")

    # Refresh prices button
    if st.button("🔄 Refresh Prices", use_container_width=True):
        with st.spinner("Fetching latest prices..."):
            portfolio.update_prices()
            # Save snapshot
            summary = portfolio.get_summary()
            db.save_portfolio_snapshot(
                summary['total_value'],
                summary['total_cost_basis'],
                summary['total_pnl'],
                portfolio.to_dict()
            )
            st.success("✅ Prices updated!")
            st.rerun()

# Main content area
if len(portfolio.positions) == 0:
    st.info("👋 Welcome! Add your first position using the sidebar to get started.")
else:
    # Update prices automatically
    portfolio.update_prices()

    # Portfolio Summary Cards
    summary = portfolio.get_summary()

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label="Total Value",
            value=f"${summary['total_value']:,.2f}",
            delta=f"${summary['total_pnl']:,.2f}"
        )

    with col2:
        st.metric(
            label="Total Cost Basis",
            value=f"${summary['total_cost_basis']:,.2f}"
        )

    with col3:
        delta_color = "normal" if summary['total_pnl'] >= 0 else "inverse"
        st.metric(
            label="Total P&L",
            value=f"${summary['total_pnl']:,.2f}",
            delta=f"{summary['total_pnl_percent']:.2f}%"
        )

    with col4:
        st.metric(
            label="Positions",
            value=summary['num_positions']
        )

    st.markdown("---")

    # Portfolio Holdings Table
    st.subheader("📊 Portfolio Holdings")

    holdings_data = []
    for pos in portfolio.positions:
        holdings_data.append({
            'Ticker': pos.ticker,
            'Quantity': f"{pos.quantity:.2f}",
            'Entry Price': f"${pos.entry_price:.2f}",
            'Current Price': f"${pos.current_price:.2f}" if pos.current_price else "N/A",
            'Cost Basis': f"${pos.cost_basis:,.2f}",
            'Current Value': f"${pos.current_value:,.2f}",
            'P&L': f"${pos.unrealized_pnl:,.2f}",
            'P&L %': f"{pos.unrealized_pnl_percent:.2f}%"
        })

    df = pd.DataFrame(holdings_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    st.markdown("---")

    # Charts
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("🥧 Asset Allocation")
        if summary['asset_allocation']:
            fig_pie = px.pie(
                values=list(summary['asset_allocation'].values()),
                names=list(summary['asset_allocation'].keys()),
                title="Portfolio Composition by Value"
            )
            st.plotly_chart(fig_pie, use_container_width=True)

    with col2:
        st.subheader("📈 Portfolio History")
        history = db.get_portfolio_history(days=30)

        if history:
            history_df = pd.DataFrame(history)
            history_df['snapshot_date'] = pd.to_datetime(history_df['snapshot_date'])

            fig_line = go.Figure()
            fig_line.add_trace(go.Scatter(
                x=history_df['snapshot_date'],
                y=history_df['total_value'],
                mode='lines+markers',
                name='Portfolio Value',
                line=dict(color='#1f77b4', width=2)
            ))

            fig_line.update_layout(
                title="Portfolio Value Over Time",
                xaxis_title="Date",
                yaxis_title="Value ($)",
                hovermode='x unified'
            )

            st.plotly_chart(fig_line, use_container_width=True)
        else:
            st.info("No historical data yet. Click 'Refresh Prices' to start tracking!")

    st.markdown("---")

    # Recent Transactions
    st.subheader("📜 Recent Transactions")
    transactions = db.get_transactions(limit=10)

    if transactions:
        trans_data = []
        for trans in transactions:
            trans_data.append({
                'Date': datetime.fromisoformat(trans['transaction_date']).strftime('%Y-%m-%d %H:%M'),
                'Type': trans['transaction_type'],
                'Ticker': trans['ticker'],
                'Quantity': f"{trans['quantity']:.2f}",
                'Price': f"${trans['price']:.2f}",
                'Total': f"${trans['quantity'] * trans['price']:,.2f}"
            })

        trans_df = pd.DataFrame(trans_data)
        st.dataframe(trans_df, use_container_width=True, hide_index=True)
    else:
        st.info("No transactions yet")

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: gray;'>
    Built with Streamlit • Data from yfinance • Updates every refresh
    </div>
    """,
    unsafe_allow_html=True
)
