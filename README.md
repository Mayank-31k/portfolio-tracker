# Portfolio Tracker - Real-Time Investment Dashboard

A professional, real-time portfolio tracking web application built with Flask, WebSockets, and modern web technologies. Track your investments, monitor P&L, analyze performance with advanced metrics, and visualize your portfolio in a beautiful, responsive interface.

## Features

### Core Features
- **Real-time WebSocket Updates** - Automatic price updates every 30 seconds
- **Smart Stock Search** - Autocomplete search with popular stock suggestions
- **Transaction Management** - Buy and sell positions with full transaction history
- **P&L Calculation** - Real-time unrealized gains/losses for each position
- **Beautiful Modern UI** - Responsive design with smooth animations
- **Dark Mode** - Toggle between light and dark themes
- **Data Persistence** - SQLite database stores all data

### Advanced Analytics
- **Sharpe Ratio** - Risk-adjusted return metric
- **Portfolio Volatility** - Annualized standard deviation
- **Maximum Drawdown** - Largest peak-to-trough decline
- **Beta** - Market correlation analysis
- **Alpha** - Excess returns over benchmark
- **Value at Risk (VaR)** - 95% confidence risk metric

### Visualizations
- **Interactive Portfolio Chart** - Historical value tracking with Chart.js
- **Asset Allocation Pie Chart** - Visual portfolio composition
- **Real-time Summary Cards** - Total value, P&L, positions count
- **Holdings Table** - Detailed position information
- **Transaction History** - Complete audit trail

## Project Structure

```
portfolio_tracker/
├── src/
│   ├── data/
│   │   ├── price_fetcher.py      # yfinance API integration
│   │   ├── database.py            # SQLite database operations
│   │   └── stock_search.py        # Stock search & autocomplete
│   ├── portfolio/
│   │   ├── position.py            # Position class with P&L
│   │   ├── portfolio.py           # Portfolio management
│   │   └── analytics.py           # Advanced metrics (Sharpe, Beta, etc.)
├── templates/
│   └── index.html                 # Modern HTML5 frontend
├── static/
│   ├── style.css                  # Beautiful CSS with dark mode
│   └── app.js                     # Interactive JavaScript + WebSocket
├── data/                          # SQLite database (auto-created)
├── server.py                      # Flask backend with Socket.IO
├── requirements.txt               # Python dependencies
└── README.md                      # This file
```

## Technology Stack

### Backend
- **Flask** - Lightweight web framework
- **Flask-SocketIO** - Real-time WebSocket communication
- **yfinance** - Real-time stock price data
- **Pandas & NumPy** - Data analysis and calculations
- **SQLite** - Database for persistence

### Frontend
- **HTML5 & CSS3** - Modern, semantic markup
- **JavaScript (ES6+)** - Interactive functionality
- **Socket.IO Client** - Real-time updates
- **Chart.js** - Beautiful, responsive charts
- **Font Awesome** - Icon library

## Installation

1. **Clone or download this repository**

2. **Create a virtual environment (recommended)**
```bash
python -m venv venv
```

3. **Activate the virtual environment**
- Windows:
```bash
venv\Scripts\activate
```
- Mac/Linux:
```bash
source venv/bin/activate
```

4. **Install dependencies**
```bash
pip install -r requirements.txt
```

## Usage

1. **Start the server**
```bash
python server.py
```

2. **Access the dashboard**
Open your browser and go to:
```
http://localhost:5000
```

3. **Add your first position**
- Use the stock search bar to find a ticker (e.g., AAPL, GOOGL, MSFT)
- Or click on popular stock chips for quick selection
- Enter quantity and price per share
- Click "Buy Position"

4. **Watch real-time updates**
- Prices update automatically every 30 seconds
- Click the refresh button for manual updates
- Portfolio value, P&L, and charts update live

5. **Toggle dark mode**
- Click the moon/sun icon in the header
- Your preference is saved in browser

## Key Features Explained

### Real-Time Updates
The application uses WebSockets to push updates to all connected clients every 30 seconds. No need to refresh the page - your portfolio stays current automatically.

### Smart Stock Search
Start typing a ticker or company name, and get instant autocomplete suggestions. Popular stocks are pre-loaded for quick access.

### Advanced Analytics

- **Sharpe Ratio**: Measures risk-adjusted return. Higher is better (>1 is good, >2 is excellent)
- **Volatility**: Annualized standard deviation. Shows how much your portfolio value fluctuates
- **Max Drawdown**: Largest percentage drop from peak to trough. Important for risk management
- **Beta**: Correlation to market (SPY). Beta > 1 means more volatile than market
- **Alpha**: Excess return over expected return. Positive alpha means outperforming the benchmark
- **VaR (95%)**: Value at Risk at 95% confidence. Potential loss in worst 5% of scenarios

### Beautiful UI
- Gradient card backgrounds
- Smooth hover animations
- Responsive design works on all devices
- Professional color scheme
- Clean, modern typography

### Dark Mode
Toggle between light and dark themes. Dark mode reduces eye strain and looks great. Your preference is saved in local storage.

## Sample Tickers to Try

### Tech Giants
- **AAPL** - Apple Inc.
- **GOOGL** - Alphabet (Google)
- **MSFT** - Microsoft
- **NVDA** - NVIDIA
- **META** - Meta (Facebook)
- **TSLA** - Tesla

### Finance
- **JPM** - JPMorgan Chase
- **V** - Visa
- **MA** - Mastercard
- **BAC** - Bank of America

### ETFs
- **SPY** - S&P 500 ETF
- **QQQ** - Nasdaq-100 ETF
- **VTI** - Total Stock Market

### Crypto
- **BTC-USD** - Bitcoin
- **ETH-USD** - Ethereum

## API Endpoints

The Flask backend provides a RESTful API:

- `GET /api/portfolio` - Get full portfolio data
- `POST /api/positions` - Add a new position
- `DELETE /api/positions/<ticker>` - Remove a position
- `GET /api/search?q=<query>` - Search for stocks
- `GET /api/stock/<ticker>` - Get stock information
- `GET /api/analytics` - Get advanced analytics
- `GET /api/history?days=<n>` - Get portfolio history
- `GET /api/transactions?limit=<n>` - Get transaction history
- `POST /api/refresh` - Manually refresh all prices

## WebSocket Events

Real-time events pushed to clients:

- `portfolio_update` - Portfolio data updated
- `position_added` - New position added
- `position_removed` - Position removed
- `prices_refreshed` - Prices manually refreshed
- `connected` - Client connected to server

## Skills Demonstrated

This project showcases:

1. **Full-Stack Development** - Backend API + Frontend UI
2. **Real-Time Communication** - WebSockets for live updates
3. **Financial Domain Knowledge** - P&L, Sharpe ratio, beta, alpha, VaR
4. **Data Visualization** - Interactive charts with Chart.js
5. **Modern UI/UX** - Responsive design, dark mode, animations
6. **Database Design** - SQLite schema for positions, transactions, snapshots
7. **API Design** - RESTful endpoints with proper error handling
8. **Asynchronous Programming** - Background tasks for price updates
9. **Production Practices** - Error handling, logging, validation

## Interview Talking Points

- "Built full-stack web application with Flask backend and vanilla JavaScript frontend"
- "Implemented real-time WebSocket communication for live portfolio updates"
- "Calculated advanced financial metrics: Sharpe ratio, alpha, beta, VaR, max drawdown"
- "Designed responsive UI with dark mode and smooth animations"
- "Used Chart.js for interactive data visualizations"
- "Implemented autocomplete stock search with debouncing"
- "Created RESTful API with proper error handling and validation"
- "Built background task system for automatic price updates every 30 seconds"

## Troubleshooting

**Issue: Port 5000 already in use**
```bash
# Change port in server.py line 393
socketio.run(app, host='0.0.0.0', port=5001)
```

**Issue: Ticker not found**
- Verify ticker symbol is correct (uppercase)
- Try with exchange suffix (e.g., BTC-USD for crypto)
- Check if yfinance supports the ticker

**Issue: Prices not updating**
- Check internet connection
- Verify yfinance API is accessible
- Check browser console for WebSocket connection errors

**Issue: Charts not displaying**
- Check browser console for errors
- Ensure Chart.js CDN is accessible
- Try hard refresh (Ctrl+Shift+R)

## Future Enhancements

Potential features to add:

- [ ] Multi-currency portfolio support
- [ ] Dividend tracking and reinvestment
- [ ] Price alerts and notifications
- [ ] Export to Excel/PDF reports
- [ ] User authentication and multiple portfolios
- [ ] Benchmark comparison charts
- [ ] Correlation heatmap
- [ ] News feed integration
- [ ] Options and derivatives tracking
- [ ] Tax reporting (cost basis, realized gains)

## License

MIT License - Feel free to use for personal projects and portfolios

## Contributing

This is a portfolio project, but suggestions and improvements are welcome!

## Author

Built to demonstrate full-stack development skills for trading and financial technology roles.

---

**Note**: This application uses real market data via yfinance. Market data may be delayed 15-20 minutes depending on exchange. Not intended for production trading.
