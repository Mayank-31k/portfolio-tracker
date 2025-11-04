#!/bin/bash

# Portfolio Tracker - Run Script

echo "🚀 Starting Portfolio Tracker..."
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Run the application
echo ""
echo "✨ Launching Portfolio Tracker Dashboard..."
echo "🌐 Open your browser to http://localhost:8501"
echo ""
streamlit run src/dashboard/app.py
