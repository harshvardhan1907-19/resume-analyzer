#!/bin/bash
set -o errexit

echo "🚀 Installing dependencies..."
pip install -r requirements.txt

echo "📦 Collecting static files..."
python manage.py collectstatic --no-input

echo "🗄️ Running migrations..."
# Create database tables if they don't exist
python manage.py migrate --no-input

echo "✅ Build completed!"