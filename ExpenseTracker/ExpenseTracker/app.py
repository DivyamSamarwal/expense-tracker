import os
import logging
from datetime import datetime
from flask import Flask, session, request, jsonify
from markupsafe import Markup
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Initialize Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "dev_key_for_expense_tracker")

# Configure SQLAlchemy
database_url = os.environ.get("DATABASE_URL")
if database_url and database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)
# Prefer database inside the Flask `instance/` folder for runtime data.
# Ensure the instance folder exists and use an absolute path for SQLite.
basedir = os.path.dirname(__file__)
instance_dir = os.path.join(basedir, 'instance')
os.makedirs(instance_dir, exist_ok=True)
instance_db_path = os.path.join(instance_dir, 'expense_tracker.db')
if not database_url or "neondb_owner" in database_url:
    abs_path = os.path.abspath(instance_db_path).replace('\\', '/')
    database_url = f"sqlite:///{abs_path}"
    
app.config['SQLALCHEMY_DATABASE_URI'] = database_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

if database_url.startswith("postgresql://"):
    app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
        "pool_recycle": 300,
        "pool_pre_ping": True,
    }

# Initialize SQLAlchemy
db = SQLAlchemy(app)

# Initialize flask-login
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))


# Jinja filter to format amounts in Indian Rupee style (₹ and Indian grouping)
# Supported currencies (symbol + locale)
CURRENCY_OPTIONS = {
    'INR': {'symbol': '&#8377;', 'locale': 'en-IN'},
    'USD': {'symbol': '$', 'locale': 'en-US'},
    'EUR': {'symbol': '€', 'locale': 'de-DE'},
    'GBP': {'symbol': '£', 'locale': 'en-GB'},
    'JPY': {'symbol': '¥', 'locale': 'ja-JP'},
    'AUD': {'symbol': '$', 'locale': 'en-AU'},
}


def format_currency(value):
    try:
        amount = float(value)
    except Exception:
        return value
    # Determine currency code from session or default to INR
    code = session.get('currency', 'INR')
    # Special-case INR to use Indian-style grouping
    negative = amount < 0
    amount = abs(amount)

    if code == 'INR':
        whole = int(amount)
        fraction = int(round((amount - whole) * 100))

        whole_str = str(whole)
        if len(whole_str) > 3:
            last3 = whole_str[-3:]
            rest = whole_str[:-3]
            rest_groups = []
            while len(rest) > 2:
                rest_groups.insert(0, rest[-2:])
                rest = rest[:-2]
            if rest:
                rest_groups.insert(0, rest)
            formatted_whole = ','.join(rest_groups) + ',' + last3
        else:
            formatted_whole = whole_str

        formatted = f"{formatted_whole}.{fraction:02d}"
        if negative:
            formatted = f"-{formatted}"
        symbol = CURRENCY_OPTIONS.get('INR', {}).get('symbol', '&#8377;')
        return Markup(f"{symbol}{formatted}")

    # Fallback formatting for other currencies (western grouping)
    formatted = f"{amount:,.2f}"
    if negative:
        formatted = f"-{formatted}"
    symbol = CURRENCY_OPTIONS.get(code, {}).get('symbol', code + ' ')
    return Markup(f"{symbol}{formatted}")

# Register filter
app.jinja_env.filters['currency'] = format_currency


@app.context_processor
def inject_currency():
    code = session.get('currency', 'INR')
    symbol = CURRENCY_OPTIONS.get(code, {}).get('symbol', '')
    return dict(current_currency=code, current_currency_symbol=Markup(symbol))


@app.route('/set_currency', methods=['POST'])
def set_currency():
    data = {}
    try:
        data = request.get_json() or {}
    except Exception:
        data = request.form or {}
    code = data.get('currency')
    if code and code in CURRENCY_OPTIONS:
        session['currency'] = code
        return jsonify(success=True, currency=code)
    return jsonify(success=False), 400
