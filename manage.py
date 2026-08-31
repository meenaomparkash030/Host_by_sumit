#!/usr/bin/env python3
import os
import sys
import argparse
from app import app, db_query, init_db

def main():
    parser = argparse.ArgumentParser(description='SHAPPNO VPS Management')
    parser.add_argument('command', help='Command to run')
    parser.add_argument('--username', help='Username for commands')
    parser.add_argument('--password', help='Password for commands')
    
    args = parser.parse_args()
    
    if args.command == 'init_db':
        init_db()
        print("✅ Database initialized")
    
    elif args.command == 'create_admin':
        if not args.username or not args.password:
            print("❌ --username and --password required")
            return
        from werkzeug.security import generate_password_hash
        hashed = generate_password_hash(args.password)
        db_query('''INSERT OR REPLACE INTO users (username, password_hash, is_admin, plan, max_servers, created_at, balance)
                    VALUES (?, ?, ?, ?, ?, ?, ?)''',
                 (args.username, hashed, 1, 'enterprise', 999, datetime.now().isoformat(), 99999.0))
        print(f"✅ Admin {args.username} created")
    
    elif args.command == 'list_users':
        users = db_query('SELECT username, plan, balance, is_admin FROM users', fetch_all=True)
        for u in users:
            print(f"{u[0]} - {u[1]} - ${u[2]} - {'Admin' if u[3] else 'User'}")
    
    else:
        print(f"❌ Unknown command: {args.command}")

if __name__ == '__main__':
    main()