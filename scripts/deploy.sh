#!/bin/bash
# ─── SHAPPNO VPS ─── Deploy Script ─────────────────────────────────────

echo "[SHAPPNO] 🚀 Starting deployment..."

# Pull latest changes
if [ -d ".git" ]; then
    echo "[SHAPPNO] 📥 Pulling latest changes..."
    git pull
fi

# Install dependencies
echo "[SHAPPNO] 📦 Installing dependencies..."
pip install -r requirements.txt

# Run migrations (if any)
echo "[SHAPPNO] 🔄 Running migrations..."
python manage.py init_db

# Restart service
echo "[SHAPPNO] 🔄 Restarting service..."
if command -v systemctl &> /dev/null; then
    sudo systemctl restart shappno
elif command -v supervisorctl &> /dev/null; then
    supervisorctl restart shappno
else
    echo "[SHAPPNO] ⚠️ No service manager found. Restart manually."
fi

echo "[SHAPPNO] ✅ Deployment completed!"