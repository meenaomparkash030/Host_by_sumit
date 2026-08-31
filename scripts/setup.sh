#!/bin/bash
# ─── SHAPPNO VPS ─── Setup Script ─────────────────────────────────────

echo "[SHAPPNO] 🚀 Starting setup..."

# Create directories
mkdir -p data logs servers backups temp

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
python manage.py init_db

# Create admin user
python manage.py create_admin --username admin --password Sumit

# Create .env file if not exists
if [ ! -f ".env" ]; then
    echo "SECRET_KEY=$(openssl rand -hex 32)" > .env
    echo "PORT=5000" >> .env
    echo "FLASK_DEBUG=False" >> .env
    echo "PLATFORM=local" >> .env
    echo "[SHAPPNO] ✅ .env file created"
fi

echo "[SHAPPNO] ✅ Setup completed!"
echo "[SHAPPNO] 🔑 Admin: admin / Password: Sumit"
echo "[SHAPPNO] 🚀 Run: python app.py"