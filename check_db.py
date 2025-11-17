#!/usr/bin/env python3
"""Small utility to inspect SQLite DB files and warn about multiple DB locations.

Usage: python check_db.py
"""
import os
import sys
import sqlite3
from pathlib import Path


def find_dbs(root: Path):
    return list(root.rglob('expense_tracker.db'))


def get_app_db_uri():
    # Import the app to read configured SQLALCHEMY_DATABASE_URI
    sys.path.insert(0, str(Path.cwd()))
    try:
        from ExpenseTracker.app import app
        return app.config.get('SQLALCHEMY_DATABASE_URI')
    except Exception as e:
        return None


def print_db_info(path: Path):
    stat = path.stat()
    size_kb = stat.st_size / 1024
    print(f"- {path} (size: {size_kb:.1f} KB, modified: {stat.st_mtime})")


def main():
    root = Path.cwd()
    print(f"Scanning for 'expense_tracker.db' under {root}")
    dbs = find_dbs(root)
    if not dbs:
        print("No SQLite DB files named 'expense_tracker.db' found.")
        return

    for p in dbs:
        print_db_info(p)

    app_uri = get_app_db_uri()
    if app_uri:
        print(f"\nApp configured SQLALCHEMY_DATABASE_URI: {app_uri}")
        # If configured sqlite:///..., extract path
        if app_uri.startswith('sqlite:///'):
            configured_path = Path(app_uri.replace('sqlite:///', '')).resolve()
            print(f"Configured DB path resolved to: {configured_path}")
            matches = [p.resolve() == configured_path for p in dbs]
            if any(matches):
                print('Configured DB file is present in the repository. Good.')
            else:
                print('Warning: configured DB file not found among discovered DB files.')
    else:
        print('Could not import application to read configured DB URI.')


if __name__ == '__main__':
    main()
