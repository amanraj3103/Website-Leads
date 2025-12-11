#!/bin/bash

# Dream Axis Lead Collection Website - Startup Script

echo "🚀 Starting Dream Axis Lead Collection Website..."
echo ""

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3 first."
    exit 1
fi

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📥 Installing dependencies..."
pip install -q -r requirements.txt

# Start the server
echo ""
echo "✅ Starting server on http://localhost:5000"
echo "📝 Press Ctrl+C to stop the server"
echo ""
python server.py

