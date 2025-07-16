#!/bin/bash

# Setup script for Event Management System
# This script installs all dependencies for both backend and frontend

echo "🔧 Setting up Event Management System..."

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed. Please install Python 3.8+"
    exit 1
fi

# Check if pip is installed
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed. Please install pip3"
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is required but not installed. Please install Node.js 16+"
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "❌ npm is required but not installed. Please install npm"
    exit 1
fi

echo "✅ Prerequisites check passed"

# Setup backend
echo "🐍 Setting up Python backend..."
cd backend

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip3 install --upgrade pip
pip3 install -r requirements.txt

cd ..

# Setup frontend
echo "📦 Setting up Node.js frontend..."
cd frontend

# Install Node.js dependencies
echo "Installing Node.js dependencies..."
npm install

cd ..

echo "✅ Setup complete!"
echo ""
echo "To start the development servers:"
echo "  ./scripts/dev.sh"
echo ""
echo "Or use Docker Compose:"
echo "  docker-compose up --build" 