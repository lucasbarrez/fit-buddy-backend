#!/bin/bash

# Setup script for the project

echo "🚀 Setting up Oh My Match Backend..."

# Check if UV is installed
if ! command -v uv &> /dev/null
then
    echo "📦 UV is not installed. Installing UV..."
    pip install uv
fi

# Create virtual environment with UV
echo "🔧 Creating virtual environment..."
uv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source .venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
uv pip install -r pyproject.toml

# Install dev dependencies
echo "🛠️ Installing dev dependencies..."
uv pip install pytest pytest-asyncio pytest-cov httpx ruff black mypy pre-commit

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please update .env file with your actual configuration!"
fi

# Create logs directory
echo "📁 Creating logs directory..."
mkdir -p logs

# Install pre-commit hooks
echo "🪝 Installing pre-commit hooks..."
pre-commit install

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Update your .env file with actual values"
echo "2. Run 'source .venv/bin/activate' to activate the virtual environment"
echo "3. Run 'uvicorn app.main:app --reload' to start the development server"
echo "4. Visit http://localhost:8000/docs for API documentation"
