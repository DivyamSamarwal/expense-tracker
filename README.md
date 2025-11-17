# expense Tracker

A simple yet powerful Flask application to track your daily expenses, set budgets, manage recurring transactions, and work towards savings goals.

## Features

*   **Expense Tracking:** Add, edit, and delete expenses with categories, dates, and descriptions.
*   **Dashboard:** A comprehensive overview of your finances, including total spending, category breakdowns, and recent expenses.
*   **Multi-Currency Support:** Choose from various currencies (INR, USD, EUR, etc.) for display.
*   **Budgeting:** Set monthly budgets for different spending categories.
    *   Supports optional rollover balances.
*   **Recurring Transactions:** Define and manage recurring monthly expenses.
*   **Savings Goals:** Create savings goals and track your progress by making contributions.
*   **User Authentication:** Secure login and registration system.
*   **AJAX-based Edits:** Smoothly edit budgets without full page reloads.

## Prerequisites

*   [Python 3.11+](https://www.python.org/downloads/)
*   `pip` (Python package installer)
*   [Git](https://git-scm.com/downloads)

## Getting Started

Follow these steps to set up and run the application locally.

### 1. Clone the Repository

Open your terminal or PowerShell and run the following command. 

```bash
git clone <repository-url>
cd ExpenseTracker
```
*(Note: Replace `<repository-url>` with the actual URL of the GitHub repository.)*

### 2. Create and Activate a Virtual Environment

It's highly recommended to use a virtual environment to keep project dependencies isolated.

**On Windows (PowerShell):**
```powershell
# Create the virtual environment
python -m venv .venv

# Activate the virtual environment
.\.venv\Scripts\Activate.ps1
```
You will know the environment is active when you see `(.venv)` at the beginning of your terminal prompt.

**On macOS/Linux (Bash):**
```bash
# Create the virtual environment
python3 -m venv .venv

# Activate the virtual environment
source .venv/bin/activate
```

### 3. Install Dependencies

Install all the required Python packages using the `vercel-requirements.txt` file.

```powershell
pip install -r vercel-requirements.txt
```

### 4. Initialize the Database

This command will create the `expense_tracker.db` file inside an `instance` folder and set up all the necessary tables.

```powershell
python .\ExpenseTracker\init_db.py
```
You should see a message: `Database tables created successfully!`

### 5. Run the Application

Start the Flask development server.

```powershell
python .\ExpenseTracker\main.py
```

The application will be running and accessible at **http://127.0.0.1:5000**.

## How to Use

1.  **Register:** Create a new account from the registration page.
2.  **Login:** Log in with your credentials.
3.  **Add Expenses:** Navigate to the "Expenses" page to add and view your expenses.
4.  **Use the Dashboard:** Go to the "Dashboard" to:
    *   View spending summaries and charts.
    *   Set and manage budgets.
    *   Create and manage recurring transactions.
    *   Set and contribute to savings goals.
5.  **Change Currency:** Use the dropdown in the navigation bar to change the currency displayed across the application.

---
_This README was generated to provide a clear setup guide for new users._


If the script reports multiple DB files, let me know and I can consolidate or remove the unused copies for you (backups will be kept).

## Running tests / quick checks
This project does not include automated tests by default. For a basic sanity check, start the server and register a user, then add a couple of expenses and view the dashboard.

## Deployment (production)
- Do not use Flask's development server in production.
- Example (gunicorn on Linux):

```bash
# from the project root (assuming python env is prepared)
cd ExpenseTracker
gunicorn -w 4 --bind 0.0.0.0:8000 app:app
```

Also configure a proper `DATABASE_URL`, secure `SESSION_SECRET`, and use HTTPS (nginx, systemd service, etc.).

## Troubleshooting
- If the app doesn't start, check the terminal for tracebacks and ensure the venv packages were installed successfully.
- If static CSS is not applied, clear the browser cache or visit the page with a hard refresh.

## What's included
- A small helper `run.ps1` to automate setup and serving on Windows
- `init_db.py` to create tables
- A `THEME.md` documenting theme variables




