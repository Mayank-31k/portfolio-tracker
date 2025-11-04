"""
Flask backend server with WebSocket support for real-time updates
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from datetime import datetime
import sys
from pathlib import Path
import threading
import time

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.portfolio.portfolio import Portfolio
from src.portfolio.analytics import PortfolioAnalytics
from src.data.database import Database
from src.data.stock_search import StockSearch
from src.data.price_fetcher import PriceFetcher

# Initialize Flask app
app = Flask(__name__,
            template_folder='templates',
            static_folder='static')
app.config['SECRET_KEY'] = 'portfolio-tracker-secret-key-2024'
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')

# Initialize modules
db = Database()
portfolio = Portfolio()
analytics = PortfolioAnalytics()
stock_search = StockSearch()
price_fetcher = PriceFetcher()

# Load portfolio from database
def load_portfolio():
    """Load portfolio positions from database"""
    positions = db.get_all_positions()
    for pos_data in positions:
        portfolio.add_position(
            ticker=pos_data['ticker'],
            quantity=pos_data['quantity'],
            entry_price=pos_data['entry_price'],
            entry_date=datetime.fromisoformat(pos_data['entry_date'])
        )

load_portfolio()

# Background thread for real-time price updates
def background_price_update():
    """Background task to update prices every 30 seconds"""
    while True:
        try:
            if len(portfolio.positions) > 0:
                portfolio.update_prices()

                # Emit updated portfolio data to all connected clients
                socketio.emit('portfolio_update', {
                    'positions': [pos.to_dict() for pos in portfolio.positions],
                    'summary': portfolio.get_summary(),
                    'timestamp': datetime.now().isoformat()
                })

        except Exception as e:
            print(f"Error updating prices: {str(e)}")

        time.sleep(30)  # Update every 30 seconds

# Start background thread
update_thread = threading.Thread(target=background_price_update, daemon=True)
update_thread.start()


# ==================== ROUTES ====================

@app.route('/')
def index():
    """Serve main page"""
    return render_template('index.html')


@app.route('/api/portfolio', methods=['GET'])
def get_portfolio():
    """Get complete portfolio data"""
    try:
        portfolio.update_prices()

        return jsonify({
            'success': True,
            'positions': [pos.to_dict() for pos in portfolio.positions],
            'summary': portfolio.get_summary(),
            'cash_balance': db.get_cash_balance(),
            'account': db.get_account_info()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/account', methods=['GET'])
def get_account():
    """Get account information"""
    try:
        account = db.get_account_info()
        return jsonify({
            'success': True,
            'account': account
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/account/reset', methods=['POST'])
def reset_account():
    """Reset account to initial balance and clear all positions"""
    try:
        # Clear all positions
        for pos in portfolio.positions:
            db.remove_position(pos.ticker)

        portfolio.positions.clear()

        # Reset cash balance
        db.reset_account()

        return jsonify({
            'success': True,
            'message': 'Account reset to $10,000',
            'cash_balance': db.get_cash_balance()
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/positions', methods=['POST'])
def add_position():
    """Add a new position"""
    try:
        data = request.json
        ticker = data.get('ticker', '').upper()
        quantity = float(data.get('quantity', 0))
        price = float(data.get('price', 0))

        if not ticker or quantity <= 0 or price <= 0:
            return jsonify({'success': False, 'error': 'Invalid input'}), 400

        # Calculate total cost
        total_cost = quantity * price

        # Check cash balance
        cash_balance = db.get_cash_balance()
        if total_cost > cash_balance:
            return jsonify({
                'success': False,
                'error': f'Insufficient funds. You have ${cash_balance:,.2f} but need ${total_cost:,.2f}'
            }), 400

        # Validate ticker
        is_valid, error = stock_search.validate_ticker(ticker)
        if not is_valid:
            return jsonify({'success': False, 'error': error}), 400

        # Add to portfolio
        position = portfolio.add_position(ticker, quantity, price)

        # Update cash balance
        db.update_cash_balance(total_cost, 'BUY')

        # Save to database
        existing_positions = db.get_all_positions()
        ticker_exists = any(p['ticker'] == ticker for p in existing_positions)

        if ticker_exists:
            db.update_position(ticker, position.quantity, position.entry_price)
        else:
            db.add_position(ticker, quantity, price, datetime.now())

        # Add transaction
        db.add_transaction(ticker, 'BUY', quantity, price)

        # Emit update to all clients
        socketio.emit('position_added', {
            'ticker': ticker,
            'quantity': quantity,
            'price': price,
            'cash_balance': db.get_cash_balance()
        })

        return jsonify({
            'success': True,
            'position': position.to_dict(),
            'cash_balance': db.get_cash_balance()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/positions/<ticker>', methods=['DELETE'])
def remove_position(ticker):
    """Remove or reduce a position"""
    try:
        data = request.json
        quantity = data.get('quantity') if data else None

        ticker = ticker.upper()
        pos = portfolio.get_position(ticker)

        if not pos:
            return jsonify({'success': False, 'error': 'Position not found'}), 404

        # Get current price for transaction record
        current_price = pos.current_price or pos.entry_price
        actual_quantity = quantity if quantity else pos.quantity

        # Calculate proceeds from sale
        proceeds = actual_quantity * current_price

        # Update cash balance (add proceeds from sale)
        db.update_cash_balance(proceeds, 'SELL')

        # Remove from portfolio
        portfolio.remove_position(ticker, quantity)

        # Update database
        if quantity is None or quantity >= pos.quantity:
            db.remove_position(ticker)
        else:
            db.update_position(ticker, pos.quantity, pos.entry_price)

        # Add transaction
        db.add_transaction(ticker, 'SELL', actual_quantity, current_price)

        # Emit update
        socketio.emit('position_removed', {
            'ticker': ticker,
            'quantity': actual_quantity,
            'cash_balance': db.get_cash_balance()
        })

        return jsonify({
            'success': True,
            'cash_balance': db.get_cash_balance()
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/search', methods=['GET'])
def search_stocks():
    """Search for stocks"""
    try:
        query = request.args.get('q', '')
        limit = int(request.args.get('limit', 10))

        results = stock_search.search_stocks(query, limit)

        return jsonify({
            'success': True,
            'results': results
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stock/<ticker>', methods=['GET'])
def get_stock_info(ticker):
    """Get detailed stock information"""
    try:
        info = stock_search.get_stock_info(ticker.upper())

        if not info:
            return jsonify({'success': False, 'error': 'Stock not found'}), 404

        return jsonify({
            'success': True,
            'info': info
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/popular', methods=['GET'])
def get_popular_stocks():
    """Get popular stocks by category"""
    try:
        category = request.args.get('category')
        stocks = stock_search.get_popular_stocks(category)

        return jsonify({
            'success': True,
            'stocks': stocks
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/analytics', methods=['GET'])
def get_analytics():
    """Get advanced portfolio analytics"""
    try:
        if len(portfolio.positions) == 0:
            return jsonify({
                'success': True,
                'analytics': {
                    'sharpe_ratio': 0,
                    'volatility': 0,
                    'max_drawdown': 0,
                    'beta': 0,
                    'alpha': 0,
                    'var_95': 0
                }
            })

        # Get portfolio history
        history = db.get_portfolio_history(days=90)

        if len(history) < 2:
            return jsonify({
                'success': True,
                'analytics': {
                    'sharpe_ratio': 0,
                    'volatility': 0,
                    'max_drawdown': 0,
                    'beta': 0,
                    'alpha': 0,
                    'var_95': 0
                }
            })

        # Convert to pandas Series
        import pandas as pd
        values = pd.Series([h['total_value'] for h in history])
        returns = analytics.calculate_returns(values)

        # Get benchmark returns
        benchmark_returns = analytics.get_benchmark_returns('SPY', period='3mo')

        # Calculate metrics
        sharpe = analytics.calculate_sharpe_ratio(returns)
        volatility = analytics.calculate_volatility(returns)
        max_dd_pct, max_dd_val = analytics.calculate_max_drawdown(values)
        beta = analytics.calculate_beta(returns, benchmark_returns) if len(benchmark_returns) > 0 else 0
        alpha = analytics.calculate_alpha(returns, benchmark_returns) if len(benchmark_returns) > 0 else 0
        var_95 = analytics.calculate_var(returns, 0.95)

        return jsonify({
            'success': True,
            'analytics': {
                'sharpe_ratio': round(sharpe, 2),
                'volatility': round(volatility * 100, 2),
                'max_drawdown': round(max_dd_pct, 2),
                'beta': round(beta, 2),
                'alpha': round(alpha, 2),
                'var_95': round(var_95, 2)
            }
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/history', methods=['GET'])
def get_history():
    """Get portfolio value history"""
    try:
        days = int(request.args.get('days', 30))
        history = db.get_portfolio_history(days)

        return jsonify({
            'success': True,
            'history': history
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/transactions', methods=['GET'])
def get_transactions():
    """Get transaction history"""
    try:
        limit = int(request.args.get('limit', 20))
        transactions = db.get_transactions(limit=limit)

        return jsonify({
            'success': True,
            'transactions': transactions
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/refresh', methods=['POST'])
def refresh_prices():
    """Manually refresh all prices"""
    try:
        portfolio.update_prices()

        # Save snapshot
        summary = portfolio.get_summary()
        db.save_portfolio_snapshot(
            summary['total_value'],
            summary['total_cost_basis'],
            summary['total_pnl'],
            portfolio.to_dict()
        )

        # Emit update
        socketio.emit('prices_refreshed', {
            'positions': [pos.to_dict() for pos in portfolio.positions],
            'summary': summary
        })

        return jsonify({
            'success': True,
            'positions': [pos.to_dict() for pos in portfolio.positions],
            'summary': summary
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== WEBSOCKET EVENTS ====================

@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    print('Client connected')
    emit('connected', {'message': 'Connected to portfolio tracker'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    print('Client disconnected')


@socketio.on('request_update')
def handle_update_request():
    """Handle manual update request from client"""
    portfolio.update_prices()
    emit('portfolio_update', {
        'positions': [pos.to_dict() for pos in portfolio.positions],
        'summary': portfolio.get_summary(),
        'timestamp': datetime.now().isoformat()
    })


if __name__ == '__main__':
    print("Starting Portfolio Tracker Server...")
    print("Dashboard: http://localhost:5000")
    print("Real-time updates enabled")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, allow_unsafe_werkzeug=True)
