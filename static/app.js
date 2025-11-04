// ==================== SOCKET.IO CONNECTION ====================
const socket = io();

// ==================== GLOBAL VARIABLES ====================
let portfolioChart = null;
let allocationChart = null;
let searchTimeout = null;
let currentStockDetails = null;
let currentSellPosition = null;

// ==================== INIT ====================
document.addEventListener('DOMContentLoaded', () => {
    initApp();
    setupEventListeners();
    setupWebSocket();
    initCharts();
    loadData();
});

function initApp() {
    // Check for saved dark mode preference
    const darkMode = localStorage.getItem('darkMode') === 'true';
    if (darkMode) {
        document.body.setAttribute('data-theme', 'dark');
        document.querySelector('#darkModeToggle i').classList.replace('fa-moon', 'fa-sun');
    }
}

// ==================== EVENT LISTENERS ====================
function setupEventListeners() {
    // Add position form
    document.getElementById('addPositionForm').addEventListener('submit', handleAddPosition);

    // Refresh button
    document.getElementById('refreshBtn').addEventListener('click', refreshPrices);

    // Dark mode toggle
    document.getElementById('darkModeToggle').addEventListener('click', toggleDarkMode);

    // Reset account button
    document.getElementById('resetAccountBtn').addEventListener('click', resetAccount);

    // Stock search
    document.getElementById('tickerInput').addEventListener('input', handleStockSearch);

    // Close search results when clicking outside
    document.addEventListener('click', (e) => {
        if (!e.target.closest('.search-container')) {
            document.getElementById('searchResults').classList.remove('active');
        }
    });

    // Close modals when clicking outside
    window.addEventListener('click', (e) => {
        if (e.target.classList.contains('modal')) {
            e.target.style.display = 'none';
        }
    });

    // Update estimated proceeds when sell quantity changes
    const sellQuantityInput = document.getElementById('sellQuantity');
    if (sellQuantityInput) {
        sellQuantityInput.addEventListener('input', updateEstimatedProceeds);
    }
}

// ==================== WEBSOCKET ====================
function setupWebSocket() {
    socket.on('connect', () => {
        console.log('Connected to server');
        showToast('Connected to real-time updates', 'success');
    });

    socket.on('portfolio_update', (data) => {
        console.log('Portfolio updated:', data);
        updatePortfolioDisplay(data);
    });

    socket.on('position_added', (data) => {
        console.log('Position added:', data);
        showToast(`Added ${data.quantity} shares of ${data.ticker}`, 'success');
        loadData();
    });

    socket.on('position_removed', (data) => {
        console.log('Position removed:', data);
        showToast(`Removed ${data.quantity} shares of ${data.ticker}`, 'success');
        loadData();
    });

    socket.on('prices_refreshed', (data) => {
        console.log('Prices refreshed');
        updatePortfolioDisplay(data);
        showToast('Prices updated successfully', 'success');
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        showToast('Disconnected from server', 'error');
    });
}

// ==================== DATA LOADING ====================
async function loadData() {
    try {
        showLoading();

        // Load portfolio
        const portfolioResponse = await fetch('/api/portfolio');
        const portfolioData = await portfolioResponse.json();

        if (portfolioData.success) {
            updatePortfolioDisplay(portfolioData);
        }

        // Load analytics
        const analyticsResponse = await fetch('/api/analytics');
        const analyticsData = await analyticsResponse.json();

        if (analyticsData.success) {
            updateAnalytics(analyticsData.analytics);
        }

        // Load history
        const historyResponse = await fetch('/api/history?days=30');
        const historyData = await historyResponse.json();

        if (historyData.success) {
            updatePortfolioChart(historyData.history);
        }

        // Load transactions
        const transactionsResponse = await fetch('/api/transactions?limit=20');
        const transactionsData = await transactionsResponse.json();

        if (transactionsData.success) {
            updateTransactionsTable(transactionsData.transactions);
        }

    } catch (error) {
        console.error('Error loading data:', error);
        showToast('Error loading data', 'error');
    } finally {
        hideLoading();
    }
}

// ==================== PORTFOLIO DISPLAY ====================
function updatePortfolioDisplay(data) {
    const { positions, summary, cash_balance, account } = data;

    // Get cash balance
    const cashBalance = cash_balance !== undefined ? cash_balance : (account ? account.cash_balance : 10000);

    // Calculate total account value (portfolio + cash)
    const totalAccountValue = summary.total_value + cashBalance;
    const initialBalance = account ? account.initial_balance : 10000;
    const accountPnL = totalAccountValue - initialBalance;
    const accountPnLPercent = ((accountPnL / initialBalance) * 100);

    // Update cash balance
    document.getElementById('cashBalance').textContent = formatCurrency(cashBalance);

    // Update account value
    document.getElementById('accountValue').textContent = formatCurrency(totalAccountValue);
    const accountChange = document.getElementById('accountChange');
    const accountChangeSign = accountPnL >= 0 ? '+' : '';
    accountChange.textContent = `${accountChangeSign}${formatCurrency(accountPnL)} (${accountPnLPercent.toFixed(2)}%)`;
    accountChange.className = 'card-change ' + (accountPnL >= 0 ? 'positive' : 'negative');

    // Update portfolio value
    document.getElementById('totalValue').textContent = formatCurrency(summary.total_value);
    document.getElementById('costBasis').textContent = formatCurrency(summary.total_cost_basis);
    document.getElementById('totalPnL').textContent = formatCurrency(summary.total_pnl);
    document.getElementById('numPositions').textContent = summary.num_positions;

    // Update P&L percentage
    const pnlPercent = document.getElementById('pnlPercent');
    pnlPercent.textContent = `${summary.total_pnl_percent.toFixed(2)}%`;
    pnlPercent.className = 'card-change ' + (summary.total_pnl >= 0 ? 'positive' : 'negative');

    // Update total change
    const totalChange = document.getElementById('totalChange');
    const changeSign = summary.total_pnl >= 0 ? '+' : '';
    totalChange.textContent = `${changeSign}${formatCurrency(summary.total_pnl)} (${summary.total_pnl_percent.toFixed(2)}%)`;
    totalChange.className = 'card-change ' + (summary.total_pnl >= 0 ? 'positive' : 'negative');

    // Update holdings table
    updateHoldingsTable(positions);

    // Update allocation chart
    updateAllocationChart(summary.asset_allocation);
}

function updateHoldingsTable(positions) {
    const tbody = document.getElementById('holdingsBody');

    if (positions.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="9">
                    <i class="fas fa-inbox"></i>
                    <p>No positions yet. Add your first position above to get started!</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = positions.map(pos => `
        <tr>
            <td class="ticker-cell">
                <span onclick="showStockDetails('${pos.ticker}')" style="cursor: pointer; text-decoration: underline;" title="View Details">
                    ${pos.ticker}
                </span>
            </td>
            <td>${pos.quantity.toFixed(2)}</td>
            <td>${formatCurrency(pos.entry_price)}</td>
            <td>${pos.current_price ? formatCurrency(pos.current_price) : 'N/A'}</td>
            <td>${formatCurrency(pos.cost_basis)}</td>
            <td>${formatCurrency(pos.current_value)}</td>
            <td class="${pos.unrealized_pnl >= 0 ? 'positive' : 'negative'}">
                ${formatCurrency(pos.unrealized_pnl)}
            </td>
            <td class="${pos.unrealized_pnl_percent >= 0 ? 'positive' : 'negative'}">
                ${pos.unrealized_pnl_percent.toFixed(2)}%
            </td>
            <td class="action-btns">
                <button class="btn-small btn-primary" onclick="showStockDetails('${pos.ticker}')" title="View Stock Details">
                    <i class="fas fa-info-circle"></i>
                </button>
                <button class="btn-small btn-danger" onclick="openSellModal('${pos.ticker}', ${pos.quantity}, ${pos.current_price || pos.entry_price})" title="Sell Position">
                    <i class="fas fa-hand-holding-usd"></i> Sell
                </button>
            </td>
        </tr>
    `).join('');
}

function updateTransactionsTable(transactions) {
    const tbody = document.getElementById('transactionsBody');

    if (transactions.length === 0) {
        tbody.innerHTML = `
            <tr class="empty-state">
                <td colspan="6">
                    <i class="fas fa-receipt"></i>
                    <p>No transactions yet</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = transactions.map(trans => {
        const date = new Date(trans.transaction_date);
        const total = trans.quantity * trans.price;

        return `
            <tr>
                <td>${date.toLocaleDateString()} ${date.toLocaleTimeString()}</td>
                <td>
                    <span class="transaction-type ${trans.transaction_type.toLowerCase()}">
                        ${trans.transaction_type}
                    </span>
                </td>
                <td class="ticker-cell">${trans.ticker}</td>
                <td>${trans.quantity.toFixed(2)}</td>
                <td>${formatCurrency(trans.price)}</td>
                <td>${formatCurrency(total)}</td>
            </tr>
        `;
    }).join('');
}

// ==================== ANALYTICS ====================
function updateAnalytics(analytics) {
    document.getElementById('sharpeRatio').textContent = analytics.sharpe_ratio.toFixed(2);
    document.getElementById('volatility').textContent = `${analytics.volatility.toFixed(2)}%`;
    document.getElementById('maxDrawdown').textContent = `${analytics.max_drawdown.toFixed(2)}%`;
    document.getElementById('beta').textContent = analytics.beta.toFixed(2);
    document.getElementById('alpha').textContent = `${analytics.alpha.toFixed(2)}%`;
    document.getElementById('var95').textContent = `${analytics.var_95.toFixed(2)}%`;
}

// ==================== CHARTS ====================
function initCharts() {
    const ctx1 = document.getElementById('portfolioChart').getContext('2d');
    const ctx2 = document.getElementById('allocationChart').getContext('2d');

    portfolioChart = new Chart(ctx1, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: 'Portfolio Value',
                data: [],
                borderColor: '#3b82f6',
                backgroundColor: 'rgba(59, 130, 246, 0.1)',
                borderWidth: 2,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    display: false
                }
            },
            scales: {
                y: {
                    beginAtZero: false,
                    ticks: {
                        callback: function(value) {
                            return '$' + value.toLocaleString();
                        }
                    }
                }
            }
        }
    });

    allocationChart = new Chart(ctx2, {
        type: 'doughnut',
        data: {
            labels: [],
            datasets: [{
                data: [],
                backgroundColor: [
                    '#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444', '#06b6d4'
                ]
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

function updatePortfolioChart(history) {
    if (!portfolioChart || history.length === 0) return;

    const labels = history.map(h => {
        const date = new Date(h.snapshot_date);
        return date.toLocaleDateString();
    });

    const data = history.map(h => h.total_value);

    portfolioChart.data.labels = labels;
    portfolioChart.data.datasets[0].data = data;
    portfolioChart.update();
}

function updateAllocationChart(allocation) {
    if (!allocationChart || !allocation) return;

    const labels = Object.keys(allocation);
    const data = Object.values(allocation);

    allocationChart.data.labels = labels;
    allocationChart.data.datasets[0].data = data;
    allocationChart.update();
}

// ==================== ACTIONS ====================
async function handleAddPosition(e) {
    e.preventDefault();

    const ticker = document.getElementById('tickerInput').value.toUpperCase().trim();
    const quantity = parseFloat(document.getElementById('quantityInput').value);
    const price = parseFloat(document.getElementById('priceInput').value);

    if (!ticker || quantity <= 0 || price <= 0) {
        showToast('Please fill in all fields correctly', 'error');
        return;
    }

    try {
        showLoading();

        const response = await fetch('/api/positions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ ticker, quantity, price })
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Successfully added ${quantity} shares of ${ticker}`, 'success');
            document.getElementById('addPositionForm').reset();
            document.getElementById('searchResults').classList.remove('active');
            await loadData();
        } else {
            showToast(data.error || 'Error adding position', 'error');
        }

    } catch (error) {
        console.error('Error adding position:', error);
        showToast('Error adding position', 'error');
    } finally {
        hideLoading();
    }
}

async function removePosition(ticker) {
    if (!confirm(`Are you sure you want to sell all shares of ${ticker}?`)) {
        return;
    }

    try {
        showLoading();

        const response = await fetch(`/api/positions/${ticker}`, {
            method: 'DELETE'
        });

        const data = await response.json();

        if (data.success) {
            showToast(`Successfully sold all shares of ${ticker}`, 'success');
            await loadData();
        } else {
            showToast(data.error || 'Error removing position', 'error');
        }

    } catch (error) {
        console.error('Error removing position:', error);
        showToast('Error removing position', 'error');
    } finally {
        hideLoading();
    }
}

async function refreshPrices() {
    try {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.disabled = true;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt fa-spin"></i>';

        const response = await fetch('/api/refresh', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            updatePortfolioDisplay(data);
            showToast('Prices refreshed successfully', 'success');
        } else {
            showToast('Error refreshing prices', 'error');
        }

    } catch (error) {
        console.error('Error refreshing prices:', error);
        showToast('Error refreshing prices', 'error');
    } finally {
        const refreshBtn = document.getElementById('refreshBtn');
        refreshBtn.disabled = false;
        refreshBtn.innerHTML = '<i class="fas fa-sync-alt"></i>';
    }
}

// ==================== STOCK SEARCH ====================
async function handleStockSearch(e) {
    const query = e.target.value.trim();

    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }

    if (query.length < 1) {
        document.getElementById('searchResults').classList.remove('active');
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search?q=${encodeURIComponent(query)}&limit=10`);
            const data = await response.json();

            if (data.success) {
                displaySearchResults(data.results);
            }

        } catch (error) {
            console.error('Error searching stocks:', error);
        }
    }, 300);
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');

    if (results.length === 0) {
        container.innerHTML = '<div class="search-result-item">No results found</div>';
        container.classList.add('active');
        return;
    }

    container.innerHTML = results.map(stock => `
        <div class="search-result-item">
            <div onclick="selectStock('${stock.ticker}')" style="flex: 1; cursor: pointer;">
                <div class="search-result-ticker">${stock.ticker}</div>
                <div class="search-result-name">${stock.name}</div>
            </div>
            <button class="btn-icon-small" onclick="showStockDetailsFromSearch(event, '${stock.ticker}')" title="View Details">
                <i class="fas fa-info-circle"></i>
            </button>
        </div>
    `).join('');

    container.classList.add('active');
}

function showStockDetailsFromSearch(event, ticker) {
    event.stopPropagation();
    showStockDetails(ticker);
}

function selectStock(ticker) {
    document.getElementById('tickerInput').value = ticker;
    document.getElementById('searchResults').classList.remove('active');

    // Show stock details modal automatically
    showStockDetails(ticker);
}

async function fetchStockPrice(ticker) {
    try {
        const response = await fetch(`/api/stock/${ticker}`);
        const data = await response.json();

        if (data.success && data.info.current_price > 0) {
            document.getElementById('priceInput').value = data.info.current_price.toFixed(2);
        }

    } catch (error) {
        console.error('Error fetching stock price:', error);
    }
}

function setTicker(ticker) {
    document.getElementById('tickerInput').value = ticker;
    // Show stock details modal automatically
    showStockDetails(ticker);
}

// ==================== UI HELPERS ====================
function toggleDarkMode() {
    const body = document.body;
    const icon = document.querySelector('#darkModeToggle i');

    if (body.getAttribute('data-theme') === 'dark') {
        body.removeAttribute('data-theme');
        icon.classList.replace('fa-sun', 'fa-moon');
        localStorage.setItem('darkMode', 'false');
    } else {
        body.setAttribute('data-theme', 'dark');
        icon.classList.replace('fa-moon', 'fa-sun');
        localStorage.setItem('darkMode', 'true');
    }
}

function showToast(message, type = 'success') {
    const toast = document.getElementById('toast');
    toast.textContent = message;
    toast.className = `toast ${type} show`;

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

function showLoading() {
    document.getElementById('loadingOverlay').classList.add('show');
}

function hideLoading() {
    document.getElementById('loadingOverlay').classList.remove('show');
}

function formatCurrency(value) {
    return new Intl.NumberFormat('en-US', {
        style: 'currency',
        currency: 'USD'
    }).format(value);
}

// ==================== STOCK DETAILS MODAL ====================
async function showStockDetails(ticker) {
    const modal = document.getElementById('stockDetailsModal');
    const body = document.getElementById('stockDetailsBody');

    // Show modal with loading state
    modal.style.display = 'flex';
    body.innerHTML = `
        <div class="stock-details-loading">
            <i class="fas fa-spinner fa-spin"></i> Loading stock details...
        </div>
    `;

    try {
        const response = await fetch(`/api/stock/${ticker}`);
        const data = await response.json();

        if (data.success && data.info) {
            currentStockDetails = data.info;
            displayStockDetails(data.info);
        } else {
            body.innerHTML = `
                <div class="error-message">
                    <i class="fas fa-exclamation-triangle"></i>
                    <p>Unable to fetch stock details for ${ticker}</p>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error fetching stock details:', error);
        body.innerHTML = `
            <div class="error-message">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading stock details</p>
            </div>
        `;
    }
}

function displayStockDetails(info) {
    const body = document.getElementById('stockDetailsBody');

    const formatNumber = (num) => {
        if (num >= 1e12) return `$${(num / 1e12).toFixed(2)}T`;
        if (num >= 1e9) return `$${(num / 1e9).toFixed(2)}B`;
        if (num >= 1e6) return `$${(num / 1e6).toFixed(2)}M`;
        return formatCurrency(num);
    };

    // Calculate price range percentage
    const priceRange52Week = info.week_52_high - info.week_52_low;
    const currentFromLow = info.current_price - info.week_52_low;
    const rangePercent = priceRange52Week > 0 ? (currentFromLow / priceRange52Week) * 100 : 50;

    body.innerHTML = `
        <!-- Real-time Price Banner -->
        <div class="price-banner">
            <div class="price-banner-header">
                <div>
                    <h3 class="price-ticker">${info.ticker}</h3>
                    <p class="price-name">${info.name}</p>
                </div>
                <div class="live-indicator">
                    <span class="live-dot"></span>
                    <span>Real-time Price</span>
                </div>
            </div>
            <div class="price-display">
                <div class="current-price-large">${formatCurrency(info.current_price)}</div>
                <div class="price-currency">${info.currency}</div>
            </div>
            <div class="price-range">
                <div class="range-labels">
                    <span class="range-label">52W Low: ${formatCurrency(info.week_52_low)}</span>
                    <span class="range-label">52W High: ${formatCurrency(info.week_52_high)}</span>
                </div>
                <div class="range-bar">
                    <div class="range-fill" style="width: ${rangePercent}%"></div>
                    <div class="range-marker" style="left: ${rangePercent}%"></div>
                </div>
            </div>
        </div>

        <!-- Details Grid -->
        <div class="stock-details-grid">
            <div class="detail-section">
                <h3><i class="fas fa-building"></i> Company Info</h3>
                <div class="detail-row">
                    <span class="detail-label">Ticker:</span>
                    <span class="detail-value"><strong>${info.ticker}</strong></span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Name:</span>
                    <span class="detail-value">${info.name}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Sector:</span>
                    <span class="detail-value">${info.sector}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Industry:</span>
                    <span class="detail-value">${info.industry}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Exchange:</span>
                    <span class="detail-value">${info.exchange}</span>
                </div>
            </div>

            <div class="detail-section">
                <h3><i class="fas fa-chart-pie"></i> Valuation Metrics</h3>
                <div class="detail-row">
                    <span class="detail-label">Market Cap:</span>
                    <span class="detail-value">${info.market_cap ? formatNumber(info.market_cap) : 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">P/E Ratio:</span>
                    <span class="detail-value">${info.pe_ratio ? info.pe_ratio.toFixed(2) : 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Dividend Yield:</span>
                    <span class="detail-value">${info.dividend_yield ? (info.dividend_yield * 100).toFixed(2) + '%' : 'N/A'}</span>
                </div>
                <div class="detail-row">
                    <span class="detail-label">Currency:</span>
                    <span class="detail-value">${info.currency}</span>
                </div>
            </div>
        </div>
    `;
}

function closeStockDetails() {
    document.getElementById('stockDetailsModal').style.display = 'none';
    currentStockDetails = null;
}

function useStockForTrade() {
    if (currentStockDetails) {
        document.getElementById('tickerInput').value = currentStockDetails.ticker;
        document.getElementById('priceInput').value = currentStockDetails.current_price.toFixed(2);
        closeStockDetails();
        // Scroll to add position form
        document.querySelector('.action-panel').scrollIntoView({ behavior: 'smooth' });
    }
}

// ==================== SELL MODAL ====================
function openSellModal(ticker, quantity, currentPrice) {
    currentSellPosition = { ticker, quantity, currentPrice };

    document.getElementById('sellTicker').value = ticker;
    document.getElementById('sellTickerDisplay').textContent = ticker;
    document.getElementById('sellAvailableQty').textContent = quantity.toFixed(2);
    document.getElementById('sellCurrentPrice').textContent = formatCurrency(currentPrice);
    document.getElementById('sellQuantity').value = '';
    document.getElementById('sellQuantity').max = quantity;
    document.getElementById('estimatedProceeds').textContent = formatCurrency(0);

    document.getElementById('sellModal').style.display = 'flex';
}

function closeSellModal() {
    document.getElementById('sellModal').style.display = 'none';
    currentSellPosition = null;
}

function updateEstimatedProceeds() {
    if (!currentSellPosition) return;

    const quantity = parseFloat(document.getElementById('sellQuantity').value) || 0;
    const proceeds = quantity * currentSellPosition.currentPrice;
    document.getElementById('estimatedProceeds').textContent = formatCurrency(proceeds);
}

async function sellPartial() {
    if (!currentSellPosition) return;

    const quantity = parseFloat(document.getElementById('sellQuantity').value);

    if (!quantity || quantity <= 0) {
        showToast('Please enter a valid quantity', 'error');
        return;
    }

    if (quantity > currentSellPosition.quantity) {
        showToast(`Cannot sell more than ${currentSellPosition.quantity.toFixed(2)} shares`, 'error');
        return;
    }

    await executeSell(currentSellPosition.ticker, quantity);
}

async function sellAll() {
    if (!currentSellPosition) return;

    if (!confirm(`Are you sure you want to sell all ${currentSellPosition.quantity.toFixed(2)} shares of ${currentSellPosition.ticker}?`)) {
        return;
    }

    await executeSell(currentSellPosition.ticker, null);
}

async function executeSell(ticker, quantity) {
    try {
        showLoading();
        closeSellModal();

        const body = quantity ? JSON.stringify({ quantity }) : null;

        const response = await fetch(`/api/positions/${ticker}`, {
            method: 'DELETE',
            headers: body ? { 'Content-Type': 'application/json' } : {},
            body: body
        });

        const data = await response.json();

        if (data.success) {
            const qtyText = quantity ? quantity.toFixed(2) : 'all';
            showToast(`Successfully sold ${qtyText} shares of ${ticker}`, 'success');
            await loadData();
        } else {
            showToast(data.error || 'Error selling position', 'error');
        }

    } catch (error) {
        console.error('Error selling position:', error);
        showToast('Error selling position', 'error');
    } finally {
        hideLoading();
    }
}

// ==================== RESET ACCOUNT ====================
async function resetAccount() {
    if (!confirm('Are you sure you want to reset your account to $10,000? This will clear all positions and reset your cash balance.')) {
        return;
    }

    try {
        showLoading();

        const response = await fetch('/api/account/reset', {
            method: 'POST'
        });

        const data = await response.json();

        if (data.success) {
            showToast('Account reset to $10,000', 'success');
            await loadData();
        } else {
            showToast(data.error || 'Error resetting account', 'error');
        }

    } catch (error) {
        console.error('Error resetting account:', error);
        showToast('Error resetting account', 'error');
    } finally {
        hideLoading();
    }
}
