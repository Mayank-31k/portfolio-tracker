# 📈 Portfolio Tracker

A real-time portfolio tracking application built with Python, Streamlit, and yfinance. Track your stock positions, monitor P&L, and analyze portfolio performance with interactive visualizations.

## 🚀 Features

### Core Functionality
- **Real-time Price Tracking** - Live price updates using yfinance API
- **Position Management** - Add, view, and remove stock positions
- **P&L Calculation** - Real-time profit & loss tracking (realized and unrealized)
- **Portfolio Analytics** - Performance metrics including Sharpe ratio, volatility, and max drawdown
- **Data Persistence** - SQLite database for storing positions and historical data

### Dashboard Features
- 📊 Interactive portfolio overview with key metrics
- 🥧 Asset allocation pie chart
- 💰 P&L visualization by position
- 📈 Historical portfolio value tracking
- 📉 Performance analytics and risk metrics

## 🛠️ Technology Stack

- **Frontend**: Streamlit
- **Data Source**: yfinance (Yahoo Finance API)
- **Database**: SQLite
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone the repository**
```bash
git clone https://github.com/yourusername/portfolio-tracker.git
cd portfolio-tracker
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Run the application**
```bash
streamlit run src/dashboard/app.py
```

The application will open in your default browser at `http://localhost:8501`

## 📖 Usage

### Adding a Position

1. Enter the ticker symbol (e.g., AAPL, GOOGL, MSFT)
2. Enter the quantity of shares
3. Enter the entry price (purchase price per share)
4. Click "Add Position"

### Viewing Portfolio

The dashboard displays:
- **Total Value**: Current market value of all positions
- **Total Cost**: Total cost basis (amount invested)
- **Unrealized P&L**: Current profit/loss
- **Positions Table**: Detailed view of each holding

### Tracking Performance

- Click "Refresh Prices" to update current market prices
- Click "Save Portfolio Snapshot" to record historical data
- View performance metrics after collecting multiple snapshots

### Removing a Position

1. Select the position from the dropdown menu
2. Click "Remove" to close the position

## 📁 Project Structure

```
portfolio-tracker/
├── src/
│   ├── data/
│   │   ├── price_fetcher.py      # Real-time price fetching
│   │   └── database.py            # SQLite database operations
│   ├── portfolio/
│   │   ├── position.py            # Position class
│   │   ├── portfolio.py           # Portfolio management
│   │   └── analytics.py           # Performance metrics
│   └── dashboard/
│       └── app.py                 # Streamlit dashboard
├── tests/                         # Unit tests
├── data/                          # SQLite database storage
├── requirements.txt               # Python dependencies
└── README.md                      # Documentation
```

## 📊 Performance Metrics

The application calculates various portfolio metrics:

- **Total Return**: Overall portfolio return percentage
- **Volatility**: Standard deviation of returns (annualized)
- **Sharpe Ratio**: Risk-adjusted return metric
- **Max Drawdown**: Largest peak-to-trough decline
- **Win Rate**: Percentage of profitable positions
- **Average Daily Return**: Mean daily return

## 🎯 Key Skills Demonstrated

This project showcases:

1. **Financial Domain Knowledge**
   - P&L calculation and tracking
   - Risk metrics (Sharpe ratio, volatility, drawdown)
   - Portfolio management concepts

2. **Data Engineering**
   - Real-time data fetching and caching
   - Database design and operations
   - Time-series data processing

3. **Software Engineering**
   - Object-oriented design
   - Modular architecture
   - Error handling and logging
   - Clean code practices

4. **Data Visualization**
   - Interactive dashboards
   - Real-time data updates
   - Financial charts and metrics

## 🔄 Future Enhancements

Potential features for Version 2.0:

- [ ] Multi-currency support
- [ ] Benchmark comparison (S&P 500)
- [ ] Price alerts and notifications
- [ ] Transaction history view
- [ ] Export reports (PDF/Excel)
- [ ] Backtesting capabilities
- [ ] API endpoints (REST API)
- [ ] Options and derivatives support
- [ ] Dividend tracking
- [ ] Tax reporting features

## 🐛 Troubleshooting

### Common Issues

**Issue**: "No data found for ticker"
- **Solution**: Verify the ticker symbol is correct and traded on supported exchanges

**Issue**: Rate limiting errors
- **Solution**: The app implements caching to reduce API calls. Wait a few minutes between updates.

**Issue**: Database locked error
- **Solution**: Close other instances of the application

## 📝 Development

### Running Tests
```bash
pytest tests/
```

### Code Formatting
```bash
black src/
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

This project is open source and available under the MIT License.

## 👨‍💻 Author

Built as a demonstration project for quantitative trading and finance roles.

## 🙏 Acknowledgments

- [yfinance](https://github.com/ranaroussi/yfinance) for financial data
- [Streamlit](https://streamlit.io/) for the dashboard framework
- [Plotly](https://plotly.com/) for interactive visualizations

## 📧 Contact

For questions or feedback, please open an issue on GitHub.

---

**Note**: This application is for educational and portfolio tracking purposes only. It is not financial advice. Always do your own research before making investment decisions.
