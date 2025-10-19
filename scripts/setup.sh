#!/bin/bash

# Setup script for Amazon PPC Simulator
# This script will set up the development environment

set -e

echo "🚀 Setting up Amazon PPC Simulator..."
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "❌ Node.js is not installed. Please install Node.js 18+ first."
    exit 1
fi

# Check Node.js version
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18 or higher is required. Current version: $(node -v)"
    exit 1
fi

echo "✅ Prerequisites check passed"
echo ""

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env file created"
else
    echo "⚠️  .env file already exists, skipping..."
fi

# Install root dependencies
echo ""
echo "📦 Installing root dependencies..."
npm install

# Install backend dependencies
echo ""
echo "📦 Installing backend dependencies..."
cd src/backend
npm install
cd ../..

# Install frontend dependencies
echo ""
echo "📦 Installing frontend dependencies..."
cd src/frontend
npm install
cd ../..

# Generate Prisma client
echo ""
echo "🔧 Generating Prisma client..."
cd src/backend
npx prisma generate
cd ../..

# Start Docker services
echo ""
echo "🐳 Starting Docker services (PostgreSQL and Redis)..."
docker-compose up -d

# Wait for PostgreSQL to be ready
echo "⏳ Waiting for PostgreSQL to be ready..."
sleep 5

# Run database migrations
echo ""
echo "🗄️  Running database migrations..."
cd src/backend
npx prisma migrate dev --name init
cd ../..

# Seed database
echo ""
echo "🌱 Seeding database with test data..."
cd src/backend
npm run seed
cd ../..

echo ""
echo "✅ Setup completed successfully!"
echo ""
echo "📖 Next steps:"
echo "   1. Start the backend:  cd src/backend && npm run dev"
echo "   2. Start the frontend: cd src/frontend && npm run dev"
echo "   3. Open http://localhost:3000 in your browser"
echo ""
echo "📧 Test user credentials:"
echo "   Email:    demo@ppcsimulator.com"
echo "   Password: Demo123!"
echo ""
