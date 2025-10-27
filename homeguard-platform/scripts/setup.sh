#!/bin/bash

set -e

echo "🏗️  Setting up HomeGuard Platform..."

# Check prerequisites
echo "🔍 Checking prerequisites..."

if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18 or later."
    exit 1
fi

if ! command -v pnpm &> /dev/null; then
    echo "📦 Installing pnpm..."
    npm install -g pnpm
fi

if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Please install Docker."
    exit 1
fi

echo "✅ Prerequisites check passed!"

# Install dependencies
echo "📦 Installing dependencies..."
pnpm install

# Build packages
echo "🔨 Building shared packages..."
pnpm build --filter "./packages/*"

# Setup environment files
echo "⚙️  Setting up environment files..."

if [ ! -f .env ]; then
    cp .env.example .env
    echo "✅ Created root .env file"
fi

if [ ! -f apps/api/.env ]; then
    cp apps/api/.env.example apps/api/.env
    echo "✅ Created API .env file"
fi

if [ ! -f apps/web/.env.local ]; then
    cp apps/web/.env.local.example apps/web/.env.local
    echo "✅ Created Web .env.local file"
fi

if [ ! -f services/ai-engine-adapter/.env ]; then
    cp services/ai-engine-adapter/.env.example services/ai-engine-adapter/.env
    echo "✅ Created AI Engine Adapter .env file"
fi

# Start databases
echo "🐘 Starting PostgreSQL and Redis..."
docker compose up -d postgres redis

# Wait for database to be ready
echo "⏳ Waiting for database..."
sleep 5

# Run database migrations
echo "🗄️  Running database migrations..."
cd apps/api
pnpm db:generate
pnpm db:push
pnpm db:seed
cd ../..

echo ""
echo "✅ Setup complete!"
echo ""
echo "📝 Next steps:"
echo "  1. Update environment variables in .env files"
echo "  2. Run 'pnpm dev' to start development servers"
echo "  3. Access the dashboard at http://localhost:3000"
echo ""
echo "🔐 Default credentials:"
echo "  Email: admin@homeguard.com"
echo "  Password: admin123"