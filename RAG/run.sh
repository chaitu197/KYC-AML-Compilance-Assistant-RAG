#!/bin/bash

# KYC/AML RAG Chatbot - Run Script

echo "🚀 Starting KYC/AML Compliance RAG Chatbot..."
echo ""

# Check if .env file exists
if [ ! -f .env ]; then
    echo "⚠️  Warning: .env file not found!"
    echo "Please create a .env file with your Google API key:"
    echo "  cp .env.example .env"
    echo "  # Then edit .env and add your API key"
    echo ""
fi

# Check if dependencies are installed
echo "📦 Checking dependencies..."
python3 -c "import streamlit" 2>/dev/null
if [ $? -ne 0 ]; then
    echo "Installing dependencies (this may take a few minutes)..."
    pip3 install -r requirements.txt
    echo ""
fi

echo "✅ Starting Streamlit application..."
echo "📱 The app will open in your browser at http://localhost:8501"
echo ""
echo "To stop the server, press Ctrl+C"
echo ""

streamlit run app.py
