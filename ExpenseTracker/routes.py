import logging
from datetime import datetime, date
from flask import render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from app import app, db
from models import User, Expense, Budget, RecurringTransaction, SavingsGoal
from forms import ExpenseForm, LoginForm, RegistrationForm, BudgetForm, RecurringForm, GoalForm, ContributionForm

@app.route('/')
def index():
    """Redirect to login page if not logged in, otherwise show expense form"""
    if not current_user.is_authenticated:
        return redirect(url_for('login'))
    return redirect(url_for('expenses'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Handle user login"""
    if current_user.is_authenticated:
        return redirect(url_for('expenses'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            flash('Login successful!', 'success')
            return redirect(next_page or url_for('expenses'))
        else:
            flash('Login failed. Please check your email and password.', 'danger')
    
    return render_template('login.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Handle user registration"""
    if current_user.is_authenticated:
        return redirect(url_for('expenses'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', form=form)

@app.route('/logout')
def logout():
    """Handle user logout"""
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/expenses')
@login_required
def expenses():
    """Show user's expenses"""
    form = ExpenseForm()
    user_expenses = Expense.query.filter_by(user_id=current_user.id).order_by(Expense.date.desc()).all()
    return render_template('index.html', expenses=user_expenses, form=form)

@app.route('/add_expense', methods=['POST'])
@login_required
def add_expense():
    """Add a new expense"""
    form = ExpenseForm()
    
    if form.validate_on_submit():
        # Create expense object
        expense = Expense(
            amount=float(form.amount.data),
            category=form.category.data,
            date=form.date.data,
            description=form.description.data,
            user_id=current_user.id
        )
        
        # Add to database
        db.session.add(expense)
        db.session.commit()
        
        flash('Expense added successfully!', 'success')
        return redirect(url_for('expenses'))
    
    # If form validation fails
    for field, errors in form.errors.items():
        for error in errors:
            flash(f"{field}: {error}", "danger")
    
    return redirect(url_for('expenses'))

@app.route('/edit_expense/<int:expense_id>', methods=['POST'])
@login_required
def edit_expense(expense_id):
    """Edit an existing expense"""
    expense = Expense.query.get_or_404(expense_id)
    
    # Ensure the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You are not authorized to edit this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    form = ExpenseForm()
    if form.validate_on_submit():
        expense.amount = float(form.amount.data)
        expense.category = form.category.data
        expense.date = form.date.data
        expense.description = form.description.data
        
        db.session.commit()
        flash('Expense updated successfully!', 'success')
    else:
        # If form validation fails
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"{field}: {error}", "danger")
    
    return redirect(url_for('expenses'))

@app.route('/delete_expense/<int:expense_id>', methods=['POST'])
@login_required
def delete_expense(expense_id):
    """Delete an expense"""
    expense = Expense.query.get_or_404(expense_id)
    
    # Ensure the expense belongs to the current user
    if expense.user_id != current_user.id:
        flash('You are not authorized to delete this expense.', 'danger')
        return redirect(url_for('expenses'))
    
    db.session.delete(expense)
    db.session.commit()
    flash('Expense deleted successfully!', 'success')
    return redirect(url_for('expenses'))

@app.route('/filter_expenses', methods=['GET'])
@login_required
def filter_expenses():
    """Filter expenses by category and date range"""
    category = request.args.get('category')
    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    
    # Start with base query for current user
    query = Expense.query.filter_by(user_id=current_user.id)
    
    # Filter by category if provided
    if category and category != 'all':
        query = query.filter_by(category=category)
    
    # Filter by date range if provided
    if start_date_str:
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
        query = query.filter(Expense.date >= start_date)
    
    if end_date_str:
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        query = query.filter(Expense.date <= end_date)
    
    # Get filtered expenses and sort by date
    filtered_expenses = query.order_by(Expense.date.desc()).all()
    
    return render_template('index.html', expenses=filtered_expenses, form=ExpenseForm())

@app.route('/dashboard')
@login_required
def dashboard():
    """Render dashboard with expense summary"""
    # Get user's expenses
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    # Get all unique categories
    categories = {expense.category for expense in user_expenses}
    
    # Calculate total spending
    total_spent = sum(expense.amount for expense in user_expenses)
    
    # Calculate spending by category
    category_spending = {}
    for category in categories:
        category_total = sum(expense.amount for expense in user_expenses if expense.category == category)
        category_spending[category] = category_total
    
    # Budgets for user
    budgets = Budget.query.filter_by(user_id=current_user.id).all()

    # For each budget compute spent this month
    now = datetime.utcnow().date()
    def spent_this_month(category):
        return sum(e.amount for e in user_expenses if e.category == category and e.date.month == now.month and e.date.year == now.year)

    budget_status = []
    for b in budgets:
        spent = spent_this_month(b.category)
        available = b.amount + (b.rollover_balance if b.rollover else 0)
        percent = (spent / available * 100) if available > 0 else 0
        budget_status.append({'budget': b, 'spent': spent, 'available': available, 'percent': min(100, percent)})

    # Recurring transactions
    recurring = RecurringTransaction.query.filter_by(user_id=current_user.id).all()

    # Savings goals
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).all()

    return render_template(
        'dashboard.html',
        total_spent=total_spent,
        category_spending=category_spending,
        expenses=user_expenses,
        budgets=budget_status,
        recurring=recurring,
        goals=goals,
        budget_form=BudgetForm(),
        recurring_form=RecurringForm(),
        goal_form=GoalForm(),
        contribution_form=ContributionForm()
    )


@app.route('/budgets', methods=['POST'])
@login_required
def add_budget():
    form = BudgetForm()
    if form.validate_on_submit():
        b = Budget(user_id=current_user.id, category=form.category.data, amount=float(form.amount.data), rollover=bool(form.rollover.data))
        db.session.add(b)
        db.session.commit()
        flash('Budget added', 'success')
    else:
        flash('Invalid budget data', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/run_recurring', methods=['POST'])
@login_required
def run_recurring():
    # Manually trigger creation of recurring transactions due this month
    today = date.today()
    created = 0
    for r in RecurringTransaction.query.filter_by(user_id=current_user.id, active=True).all():
        # if not run this month and day matches
        if (not r.last_run) or (r.last_run.month != today.month or r.last_run.year != today.year):
            if r.day_of_month == today.day or (r.day_of_month > 28 and today.day >= 28):
                exp = Expense(amount=r.amount, category=r.category, date=today, description=(r.description or 'Recurring'), user_id=current_user.id)
                db.session.add(exp)
                r.last_run = today
                created += 1
    db.session.commit()
    flash(f'Created {created} recurring transactions', 'success')
    return redirect(url_for('dashboard'))


@app.route('/recurring', methods=['POST'])
@login_required
def add_recurring():
    form = RecurringForm()
    if form.validate_on_submit():
        r = RecurringTransaction(user_id=current_user.id, amount=float(form.amount.data), category=form.category.data, description=form.description.data, day_of_month=int(form.day_of_month.data))
        db.session.add(r)
        db.session.commit()
        flash('Recurring transaction added', 'success')
    else:
        flash('Invalid recurring data', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/create_goal', methods=['POST'])
@login_required
def create_goal():
    form = GoalForm()
    if form.validate_on_submit():
        g = SavingsGoal(user_id=current_user.id, name=form.name.data, target_amount=float(form.target_amount.data))
        db.session.add(g)
        db.session.commit()
        flash('Goal created', 'success')
    else:
        flash('Invalid goal data', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/contribute_goal/<int:goal_id>', methods=['POST'])
@login_required
def contribute_goal(goal_id):
    form = ContributionForm()
    goal = SavingsGoal.query.get_or_404(goal_id)
    if form.validate_on_submit():
        amount = float(form.amount.data)
        # Add contribution to goal
        goal.current_amount = (goal.current_amount or 0) + amount
        db.session.commit()
        flash(f'Added {amount} to {goal.name}', 'success')
    else:
        flash('Invalid contribution', 'danger')
    return redirect(url_for('dashboard'))


@app.route('/edit_budget/<int:budget_id>', methods=['POST'])
@login_required
def edit_budget(budget_id):
    b = Budget.query.get_or_404(budget_id)
    if b.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))

    # Use .get to avoid KeyError if form field is missing
    new_amount_str = request.form.get('amount')
    if new_amount_str is not None:
        try:
            b.amount = float(new_amount_str)
        except (ValueError, TypeError):
            flash('Invalid amount provided for budget.', 'danger')
            # Fallback to old amount or handle as an error
            pass

    # Checkbox values are only present in the form if they are checked
    b.rollover = 'rollover' in request.form
    
    db.session.commit()

    # If this is an AJAX request, return JSON so the frontend can update in-place
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.is_json:
        # compute spent this month for this budget's category
        today = datetime.utcnow().date()
        spent = 0.0
        for e in Expense.query.filter_by(user_id=current_user.id, category=b.category).all():
            try:
                if e.date.month == today.month and e.date.year == today.year:
                    spent += float(e.amount)
            except Exception:
                pass
        available = b.amount + (b.rollover_balance if b.rollover else 0)
        percent = min(100, (spent / available * 100) if available > 0 else 0)
        return jsonify({'success': True, 'amount': b.amount, 'rollover': b.rollover, 'spent': spent, 'available': available, 'percent': percent})

    flash('Budget updated', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_budget/<int:budget_id>', methods=['POST'])
@login_required
def delete_budget(budget_id):
    b = Budget.query.get_or_404(budget_id)
    if b.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    db.session.delete(b)
    db.session.commit()
    flash('Budget deleted', 'info')
    return redirect(url_for('dashboard'))


@app.route('/edit_recurring/<int:rec_id>', methods=['POST'])
@login_required
def edit_recurring(rec_id):
    r = RecurringTransaction.query.get_or_404(rec_id)
    if r.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))

    if 'amount' in request.form:
        try:
            r.amount = float(request.form['amount'])
        except (ValueError, TypeError):
            pass  # Keep old value if conversion fails
    
    if 'description' in request.form:
        r.description = request.form['description']

    if 'day_of_month' in request.form:
        try:
            r.day_of_month = int(request.form['day_of_month'])
        except (ValueError, TypeError):
            pass

    r.active = 'active' in request.form
    
    db.session.commit()
    flash('Recurring transaction updated', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_recurring/<int:rec_id>', methods=['POST'])
@login_required
def delete_recurring(rec_id):
    r = RecurringTransaction.query.get_or_404(rec_id)
    if r.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    db.session.delete(r)
    db.session.commit()
    flash('Recurring transaction deleted', 'info')
    return redirect(url_for('dashboard'))


@app.route('/edit_goal/<int:goal_id>', methods=['POST'])
@login_required
def edit_goal(goal_id):
    g = SavingsGoal.query.get_or_404(goal_id)
    if g.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))

    if 'name' in request.form:
        g.name = request.form['name']

    if 'target_amount' in request.form:
        try:
            g.target_amount = float(request.form['target_amount'])
        except (ValueError, TypeError):
            pass  # Keep old value if conversion fails
            
    db.session.commit()
    flash('Goal updated', 'success')
    return redirect(url_for('dashboard'))


@app.route('/delete_goal/<int:goal_id>', methods=['POST'])
@login_required
def delete_goal(goal_id):
    g = SavingsGoal.query.get_or_404(goal_id)
    if g.user_id != current_user.id:
        flash('Not authorized', 'danger')
        return redirect(url_for('dashboard'))
    db.session.delete(g)
    db.session.commit()
    flash('Goal deleted', 'info')
    return redirect(url_for('dashboard'))


@app.route('/close_month', methods=['POST'])
@login_required
def close_month():
    # For budgets with rollover enabled, compute unused and add to rollover_balance
    now = datetime.utcnow().date()
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    def spent_for_month(category, month, year):
        return sum(e.amount for e in user_expenses if e.category == category and e.date.month == month and e.date.year == year)

    budgets = Budget.query.filter_by(user_id=current_user.id).all()
    for b in budgets:
        spent = spent_for_month(b.category, now.month, now.year)
        unused = max(0.0, b.amount - spent)
        if b.rollover and unused > 0:
            b.rollover_balance = (b.rollover_balance or 0) + unused
    db.session.commit()
    flash('Month closed — rollovers applied where enabled', 'info')
    return redirect(url_for('dashboard'))

@app.route('/api/chart_data')
@login_required
def chart_data():
    """API endpoint for chart data"""
    # Get user's expenses
    user_expenses = Expense.query.filter_by(user_id=current_user.id).all()
    
    # Get all unique categories
    categories = {expense.category for expense in user_expenses}
    
    # Prepare data for chart
    category_data = []
    for category in categories:
        category_total = sum(expense.amount for expense in user_expenses if expense.category == category)
        category_data.append({
            'category': category,
            'amount': category_total
        })
    
    return jsonify(category_data)