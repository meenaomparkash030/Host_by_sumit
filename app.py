#!/usr/bin/env python3
# ─── SHAPPNO VPS ─── RENDER EDITION ────────────────────────────────────

import os
import json
import sqlite3
import secrets
import shutil
import zipfile
import time
from pathlib import Path
from functools import wraps
from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, send_file
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

# ─── PATHS ──────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / 'data'
DATA_DIR.mkdir(exist_ok=True)

DB_PATH = DATA_DIR / 'shappno.db'
SERVERS_DIR = DATA_DIR / 'servers'
BACKUP_DIR = DATA_DIR / 'backups'
TEMP_DIR = DATA_DIR / 'temp'

for d in [SERVERS_DIR, BACKUP_DIR, TEMP_DIR]:
    d.mkdir(parents=True, exist_ok=True)

# ─── APP INIT ──────────────────────────────────────────────────────────
app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', secrets.token_hex(64))
app.config['MAX_CONTENT_LENGTH'] = 500 * 1024 * 1024

# ─── DATABASE ──────────────────────────────────────────────────────────
def init_db():
    conn = sqlite3.connect(str(DB_PATH))
    c = conn.cursor()
    
    # Users
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        email TEXT,
        plan TEXT DEFAULT 'free',
        max_servers INTEGER DEFAULT 3,
        is_admin INTEGER DEFAULT 0,
        is_banned INTEGER DEFAULT 0,
        created_at TEXT,
        balance REAL DEFAULT 0
    )''')
    
    # Redeem Codes
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE NOT NULL,
        amount REAL NOT NULL,
        created_by TEXT,
        created_at TEXT,
        expires_at TEXT,
        max_uses INTEGER DEFAULT 1,
        used_count INTEGER DEFAULT 0,
        active INTEGER DEFAULT 1
    )''')
    
    # Redeem History
    c.execute('''CREATE TABLE IF NOT EXISTS redeem_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT NOT NULL,
        username TEXT NOT NULL,
        amount REAL NOT NULL,
        redeemed_at TEXT
    )''')
    
    # Transactions
    c.execute('''CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        type TEXT NOT NULL,
        amount REAL NOT NULL,
        description TEXT,
        balance_before REAL,
        balance_after REAL,
        created_at TEXT
    )''')
    
    # Servers
    c.execute('''CREATE TABLE IF NOT EXISTS servers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT UNIQUE NOT NULL,
        owner TEXT NOT NULL,
        runtime TEXT DEFAULT 'python',
        status TEXT DEFAULT 'stopped',
        main_file TEXT,
        port INTEGER DEFAULT 8080,
        created_at TEXT,
        description TEXT
    )''')
    
    # Announcements
    c.execute('''CREATE TABLE IF NOT EXISTS announcements (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        content TEXT,
        priority INTEGER DEFAULT 0,
        created_at TEXT,
        expires_at TEXT
    )''')
    
    # ─── Admin ──────────────────────────────────────────────────────────
    admin_hash = generate_password_hash('Sumit')
    c.execute('''INSERT OR IGNORE INTO users (username, password_hash, is_admin, plan, max_servers, created_at, balance)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''',
              ('admin', admin_hash, 1, 'enterprise', 999, datetime.now().isoformat(), 99999.0))
    
    conn.commit()
    conn.close()

init_db()

# ─── DB HELPERS ──────────────────────────────────────────────────────
def db_query(query, params=(), fetch_one=False, fetch_all=False):
    try:
        conn = sqlite3.connect(str(DB_PATH))
        conn.row_factory = sqlite3.Row
        c = conn.cursor()
        c.execute(query, params)
        result = None
        if fetch_one:
            result = c.fetchone()
        elif fetch_all:
            result = c.fetchall()
        conn.commit()
        conn.close()
        return result
    except Exception as e:
        return None

def get_user(username):
    return db_query('SELECT * FROM users WHERE username = ?', (username,), fetch_one=True)

def add_transaction(username, type, amount, description):
    user = get_user(username)
    if not user:
        return False
    balance_before = user['balance'] or 0
    balance_after = balance_before + amount
    db_query('UPDATE users SET balance = ? WHERE username = ?', (balance_after, username))
    db_query('''INSERT INTO transactions (username, type, amount, description, balance_before, balance_after, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)''',
             (username, type, amount, description, balance_before, balance_after, datetime.now().isoformat()))
    return True

def generate_redeem_code(length=8):
    return secrets.token_hex(length).upper()

# ─── DECORATORS ──────────────────────────────────────────────────────
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        user = get_user(session['username'])
        if user and user['is_banned'] == 1:
            session.clear()
            return redirect(url_for('login', error='Account banned'))
        return f(*args, **kwargs)
    return decorated

def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get('username'):
            return redirect(url_for('login'))
        user = get_user(session['username'])
        if not user or user['is_admin'] != 1:
            return 'Access denied', 403
        return f(*args, **kwargs)
    return decorated

# ─── ROUTES ──────────────────────────────────────────────────────────
@app.route('/')
def index():
    if session.get('username'):
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = request.args.get('error')
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        if not username or not password:
            return render_template('login.html', error='Username and password required')
        
        user = get_user(username)
        if not user:
            hashed = generate_password_hash(password)
            db_query('''INSERT INTO users (username, password_hash, plan, max_servers, created_at)
                        VALUES (?, ?, ?, ?, ?)''',
                     (username, hashed, 'free', 3, datetime.now().isoformat()))
        else:
            if user['is_banned'] == 1:
                return render_template('login.html', error='Account banned')
            if not check_password_hash(user['password_hash'], password):
                return render_template('login.html', error='Invalid password')
        
        session['username'] = username
        return redirect(url_for('dashboard'))
    return render_template('login.html', error=error, platform='render')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── DASHBOARD ──────────────────────────────────────────────────────
@app.route('/dashboard')
@login_required
def dashboard():
    user = get_user(session['username'])
    servers = db_query('SELECT * FROM servers WHERE owner = ?', (session['username'],), fetch_all=True) or []
    running = sum(1 for s in servers if s['status'] == 'running')
    announcements = db_query('SELECT * FROM announcements WHERE expires_at IS NULL OR expires_at > datetime("now") ORDER BY priority DESC LIMIT 3', fetch_all=True) or []
    
    return render_template('dashboard.html',
                         username=session['username'],
                         servers={s['name']: {'status': s['status'], 'runtime': s['runtime'], 
                                 'main_file': s['main_file'], 'port': s['port']} for s in servers},
                         running=running,
                         total=len(servers),
                         plan=user['plan'] if user else 'free',
                         max_servers=user['max_servers'] if user else 3,
                         is_admin=user['is_admin'] if user else 0,
                         balance=user['balance'] if user else 0,
                         announcements=announcements,
                         platform='render')

# ─── ADMIN PANEL ──────────────────────────────────────────────────────
@app.route('/admin')
@admin_required
def admin_panel():
    users = db_query('SELECT * FROM users ORDER BY created_at DESC', fetch_all=True) or []
    servers = db_query('SELECT * FROM servers', fetch_all=True) or []
    announcements = db_query('SELECT * FROM announcements ORDER BY created_at DESC', fetch_all=True) or []
    transactions = db_query('SELECT * FROM transactions ORDER BY created_at DESC LIMIT 100', fetch_all=True) or []
    redeem_codes = db_query('SELECT * FROM redeem_codes ORDER BY created_at DESC', fetch_all=True) or []
    
    return render_template('admin.html',
                         users=users, servers=servers, total_servers=len(servers),
                         running_servers=sum(1 for s in servers if s['status'] == 'running'),
                         total_users=len(users), announcements=announcements,
                         transactions=transactions, redeem_codes=redeem_codes,
                         platform='render')

@app.route('/admin/user/<username>/ban', methods=['POST'])
@admin_required
def admin_ban_user(username):
    if username == 'admin':
        return jsonify({'success': False, 'error': 'Cannot ban admin'})
    db_query('UPDATE users SET is_banned = 1 WHERE username = ?', (username,))
    return jsonify({'success': True})

@app.route('/admin/user/<username>/unban', methods=['POST'])
@admin_required
def admin_unban_user(username):
    db_query('UPDATE users SET is_banned = 0 WHERE username = ?', (username,))
    return jsonify({'success': True})

@app.route('/admin/user/<username>/delete', methods=['POST'])
@admin_required
def admin_delete_user(username):
    if username == 'admin':
        return jsonify({'success': False, 'error': 'Cannot delete admin'})
    db_query('DELETE FROM servers WHERE owner = ?', (username,))
    db_query('DELETE FROM users WHERE username = ?', (username,))
    return jsonify({'success': True})

@app.route('/admin/user/<username>/plan', methods=['POST'])
@admin_required
def admin_change_plan(username):
    plan = request.json.get('plan', 'free')
    max_servers = {'free': 3, 'pro': 10, 'business': 50, 'enterprise': 999}.get(plan, 3)
    db_query('UPDATE users SET plan = ?, max_servers = ? WHERE username = ?', (plan, max_servers, username))
    return jsonify({'success': True})

@app.route('/admin/balance/add', methods=['POST'])
@admin_required
def admin_add_balance():
    username = request.json.get('username', '')
    amount = float(request.json.get('amount', 0))
    if not username or amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid data'})
    user = get_user(username)
    if not user:
        return jsonify({'success': False, 'error': 'User not found'})
    if add_transaction(username, 'admin_add', amount, 'Admin added balance'):
        return jsonify({'success': True, 'new_balance': get_user(username)['balance']})
    return jsonify({'success': False, 'error': 'Failed'})

@app.route('/admin/balance/remove', methods=['POST'])
@admin_required
def admin_remove_balance():
    username = request.json.get('username', '')
    amount = float(request.json.get('amount', 0))
    if not username or amount <= 0:
        return jsonify({'success': False, 'error': 'Invalid data'})
    user = get_user(username)
    if not user or user['balance'] < amount:
        return jsonify({'success': False, 'error': 'Insufficient balance'})
    if add_transaction(username, 'admin_remove', -amount, 'Admin removed balance'):
        return jsonify({'success': True, 'new_balance': get_user(username)['balance']})
    return jsonify({'success': False, 'error': 'Failed'})

# ─── REDEEM CODE ──────────────────────────────────────────────────────
@app.route('/admin/redeem/create', methods=['POST'])
@admin_required
def admin_create_redeem_code():
    amount = float(request.json.get('amount', 0))
    max_uses = int(request.json.get('max_uses', 1))
    expires_in = int(request.json.get('expires_in', 30))
    if amount <= 0:
        return jsonify({'success': False, 'error': 'Amount must be positive'})
    
    code = generate_redeem_code(8)
    expires_at = (datetime.now() + timedelta(days=expires_in)).isoformat()
    
    db_query('''INSERT INTO redeem_codes (code, amount, created_by, created_at, expires_at, max_uses)
                VALUES (?, ?, ?, ?, ?, ?)''',
             (code, amount, session['username'], datetime.now().isoformat(), expires_at, max_uses))
    
    return jsonify({'success': True, 'code': code, 'amount': amount})

@app.route('/redeem', methods=['POST'])
@login_required
def redeem_code():
    code = request.json.get('code', '').strip().upper()
    if not code:
        return jsonify({'success': False, 'error': 'Code required'})
    
    redeem = db_query('SELECT * FROM redeem_codes WHERE code = ?', (code,), fetch_one=True)
    if not redeem:
        return jsonify({'success': False, 'error': 'Invalid code'})
    
    if redeem['active'] != 1:
        return jsonify({'success': False, 'error': 'Code inactive'})
    if redeem['expires_at'] and redeem['expires_at'] < datetime.now().isoformat():
        return jsonify({'success': False, 'error': 'Code expired'})
    if redeem['used_count'] >= redeem['max_uses']:
        return jsonify({'success': False, 'error': 'Code used'})
    
    used = db_query('SELECT * FROM redeem_history WHERE code = ? AND username = ?', 
                    (code, session['username']), fetch_one=True)
    if used:
        return jsonify({'success': False, 'error': 'Already used'})
    
    amount = redeem['amount']
    if add_transaction(session['username'], 'redeem', amount, f'Redeemed code: {code}'):
        db_query('UPDATE redeem_codes SET used_count = used_count + 1 WHERE code = ?', (code,))
        db_query('INSERT INTO redeem_history (code, username, amount, redeemed_at) VALUES (?, ?, ?, ?)',
                 (code, session['username'], amount, datetime.now().isoformat()))
        return jsonify({'success': True, 'amount': amount, 'balance': get_user(session['username'])['balance']})
    
    return jsonify({'success': False, 'error': 'Redeem failed'})

# ─── SERVER CRUD ──────────────────────────────────────────────────────
@app.route('/server/create', methods=['POST'])
@login_required
def create_server():
    name = request.form.get('name', '').strip().replace(' ', '-')
    runtime = request.form.get('runtime', 'python')
    description = request.form.get('description', '')
    if not name:
        return redirect(url_for('dashboard'))
    
    user = get_user(session['username'])
    max_servers = user['max_servers'] if user else 3
    current = db_query('SELECT COUNT(*) FROM servers WHERE owner = ?', (session['username'],), fetch_one=True)[0] or 0
    
    if current >= max_servers:
        return redirect(url_for('dashboard', error='Server limit reached'))
    
    existing = get_server(name)
    if existing:
        return redirect(url_for('dashboard', error='Server already exists'))
    
    db_query('''INSERT INTO servers (name, owner, runtime, status, created_at, description)
                VALUES (?, ?, ?, ?, ?, ?)''',
             (name, session['username'], runtime, 'stopped', datetime.now().isoformat(), description))
    
    (SERVERS_DIR / name / 'extracted').mkdir(parents=True, exist_ok=True)
    return redirect(url_for('server_detail', name=name))

@app.route('/server/delete/<name>', methods=['POST'])
@login_required
def delete_server(name):
    server = get_server(name)
    if not server or (server['owner'] != session['username'] and session['username'] != 'admin'):
        return redirect(url_for('dashboard'))
    
    db_query('DELETE FROM servers WHERE name = ?', (name,))
    shutil.rmtree(SERVERS_DIR / name, ignore_errors=True)
    return redirect(url_for('dashboard'))

@app.route('/server/<name>')
@login_required
def server_detail(name):
    server = get_server(name)
    if not server or (server['owner'] != session['username'] and session['username'] != 'admin'):
        return 'Not found', 404
    
    extract_dir = SERVERS_DIR / name / 'extracted'
    files = []
    if extract_dir.exists():
        for f in sorted(extract_dir.iterdir(), key=lambda x: (x.is_file(), x.name)):
            files.append({'name': f.name, 'path': str(f.relative_to(extract_dir)), 
                         'type': 'dir' if f.is_dir() else 'file', 'size': f.stat().st_size if f.is_file() else 0})
    
    return render_template('server.html', server_name=name, 
                         config={'status': server['status'], 'runtime': server['runtime'], 
                                 'main_file': server['main_file'], 'port': server['port']},
                         files=files, platform='render')

@app.route('/server/<name>/upload', methods=['POST'])
@login_required
def upload_file(name):
    server = get_server(name)
    if not server:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    if 'file' not in request.files:
        return jsonify({'success': False, 'error': 'No file'})
    
    f = request.files['file']
    extract_dir = SERVERS_DIR / name / 'extracted'
    extract_dir.mkdir(parents=True, exist_ok=True)
    
    temp_path = TEMP_DIR / f"{secrets.token_hex(8)}_{secure_filename(f.filename)}"
    f.save(temp_path)
    
    if f.filename.endswith('.zip'):
        try:
            with zipfile.ZipFile(temp_path, 'r') as z:
                z.extractall(extract_dir)
            temp_path.unlink()
            return jsonify({'success': True, 'files': [m.filename for m in z.infolist() if not m.is_dir()]})
        except Exception as e:
            return jsonify({'success': False, 'error': str(e)})
    else:
        dest = extract_dir / secure_filename(f.filename)
        shutil.move(temp_path, dest)
        if not server['main_file'] and f.filename.endswith(('.py', '.js', '.php', '.html')):
            db_query('UPDATE servers SET main_file = ? WHERE name = ?', (f.filename, name))
        return jsonify({'success': True, 'files': [f.filename]})

@app.route('/server/<name>/start', methods=['POST'])
@login_required
def start_server(name):
    server = get_server(name)
    if not server:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    db_query('UPDATE servers SET status = ? WHERE name = ?', ('running', name))
    return jsonify({'success': True})

@app.route('/server/<name>/stop', methods=['POST'])
@login_required
def stop_server(name):
    server = get_server(name)
    if not server:
        return jsonify({'success': False, 'error': 'Not found'}), 404
    
    db_query('UPDATE servers SET status = ? WHERE name = ?', ('stopped', name))
    return jsonify({'success': True})

@app.route('/api/stats')
def stats():
    return jsonify({'cpu': 0, 'ram': 0, 'disk': 0, 'platform': 'render'})

@app.route('/api/health')
def health():
    return jsonify({'status': 'healthy', 'platform': 'render'})

# ─── RUN ──────────────────────────────────────────────────────────────
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)