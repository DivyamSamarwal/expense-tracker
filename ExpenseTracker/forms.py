from flask_wtf import FlaskForm
from wtforms import FloatField, StringField, DateField, TextAreaField, SelectField, PasswordField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Email, EqualTo, Length, ValidationError
from models import User

class ExpenseForm(FlaskForm):
    """Form for adding and editing expenses"""
    amount = FloatField('Amount', validators=[
        DataRequired(message="Please enter an amount"),
        NumberRange(min=0.01, message="Amount must be greater than 0")
    ])
    
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('food', 'Food & Dining'),
        ('transportation', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('housing', 'Housing'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('education', 'Education'),
        ('personal', 'Personal Care'),
        ('travel', 'Travel'),
        ('other', 'Other')
    ])
    
    date = DateField('Date', validators=[DataRequired(message="Please enter a valid date")])
    
    description = TextAreaField('Description', validators=[
        DataRequired(message="Please provide a description")
    ])

class LoginForm(FlaskForm):
    """Form for user login"""
    email = StringField('Email', validators=[
        DataRequired(message="Please enter your email"),
        Email(message="Please enter a valid email address")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter your password")
    ])
    remember_me = BooleanField('Remember Me')

class RegistrationForm(FlaskForm):
    """Form for user registration"""
    username = StringField('Username', validators=[
        DataRequired(message="Please enter a username"),
        Length(min=3, max=64, message="Username must be between 3 and 64 characters")
    ])
    email = StringField('Email', validators=[
        DataRequired(message="Please enter your email"),
        Email(message="Please enter a valid email address"),
        Length(max=120, message="Email must be less than 120 characters")
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message="Please enter a password"),
        Length(min=8, message="Password must be at least 8 characters long")
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(message="Please confirm your password"),
        EqualTo('password', message="Passwords must match")
    ])
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('Username already taken. Please choose a different one.')
    
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('Email already registered. Please use a different one.')


class BudgetForm(FlaskForm):
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('food', 'Food & Dining'),
        ('transportation', 'Transportation'),
        ('entertainment', 'Entertainment'),
        ('utilities', 'Utilities'),
        ('housing', 'Housing'),
        ('healthcare', 'Healthcare'),
        ('shopping', 'Shopping'),
        ('education', 'Education'),
        ('personal', 'Personal Care'),
        ('travel', 'Travel'),
        ('other', 'Other')
    ])
    amount = FloatField('Monthly Amount', validators=[DataRequired(), NumberRange(min=0.0)])
    rollover = BooleanField('Allow rollover of unused funds')


class RecurringForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.0)])
    category = SelectField('Category', validators=[DataRequired()], choices=[
        ('housing', 'Housing'),
        ('utilities', 'Utilities'),
        ('subscription', 'Subscription'),
        ('other', 'Other')
    ])
    description = StringField('Description', validators=[Length(max=200)])
    day_of_month = SelectField('Day of month', coerce=int, choices=[(i, str(i)) for i in range(1,29)])


class GoalForm(FlaskForm):
    name = StringField('Goal name', validators=[DataRequired(), Length(max=120)])
    target_amount = FloatField('Target amount', validators=[DataRequired(), NumberRange(min=0.01)])


class ContributionForm(FlaskForm):
    amount = FloatField('Amount', validators=[DataRequired(), NumberRange(min=0.01)])
    source_category = SelectField('From category', validators=[DataRequired()], choices=[
        ('wants', 'Wants'),
        ('savings', 'Savings'),
        ('other', 'Other')
    ])
