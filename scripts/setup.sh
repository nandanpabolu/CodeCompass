#!/bin/bash

# CodeCompass Setup Script

set -e

echo "🧭 Setting up CodeCompass..."

# Check if Python 3.12+ is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is not installed. Please install Python 3.12+ first."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
REQUIRED_VERSION="3.11"

if [ "$(printf '%s\n' "$REQUIRED_VERSION" "$PYTHON_VERSION" | sort -V | head -n1)" != "$REQUIRED_VERSION" ]; then
    echo "❌ Python $REQUIRED_VERSION+ is required. Found: $PYTHON_VERSION"
    exit 1
fi

echo "✅ Python $PYTHON_VERSION found"

# Create virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️ Upgrading pip..."
pip install --upgrade pip

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Install development dependencies
echo "🛠️ Installing development dependencies..."
pip install -r requirements-dev.txt

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs
mkdir -p indexes
mkdir -p config

# Copy example configuration
if [ ! -f "config/local.yaml" ]; then
    echo "⚙️ Creating local configuration..."
    cp config/default.yaml config/local.yaml
fi

# Set up pre-commit hooks
echo "🔗 Setting up pre-commit hooks..."
pre-commit install

echo "✅ CodeCompass setup complete!"
echo ""
echo "🚀 To get started:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the MCP server: python src/mcp_server.py"
echo "3. Or run the Streamlit dashboard: streamlit run src/streamlit_app.py"
echo ""
echo "📖 For more information, see the README.md file"
