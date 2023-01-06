from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_login import login_user, login_required, logout_user, current_user
from .models import User, Account
from werkzeug.security import generate_password_hash, check_password_hash
from . import db

auth = Blueprint('auth', __name__)


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully.', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.view_accounts'))
            else:
                flash('Incorrect password.', category='error')
        else:
            flash('Email does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        email = request.form.get('email')
        firstName = request.form.get('firstName')
        password = request.form.get('password')
        confirmPassword = request.form.get('confirmPassword')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 4 characters.', category='error')
        elif len(firstName) < 1:
            flash('First name cannot be empty.', category='error')
        elif password != confirmPassword:
            flash('Passwords do not match.', category='error')
        elif len(password) < 8:
            flash('Password must be at least 8 characters.', category='error')
        else:
            # add user to database
            new_user = User(email=email, firstName=firstName,
                            password=generate_password_hash(password, method='sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(user, remember=True)
            flash('Account has been created.', category='success')

            return redirect(url_for('views.view_accounts'))

    return render_template("sign_up.html", user=current_user)


@auth.route('/create', methods=['GET', 'POST'])
@login_required
def create_account():
    new_account = Account(user_id=current_user.id)
    db.session.add(new_account)
    db.session.commit()
    flash('Account added!', category='success')
    return redirect(url_for('views.view_accounts'))


@auth.route('/deposit', methods=['GET', 'POST'])
@login_required
def deposit():
    if request.method == 'POST':
        id = request.form.get('id')
        balance = request.form.get('balance')

        balance = int(balance)
        existing_account = Account.query.get(id)

        if existing_account and existing_account.user_id == current_user.id:
            if balance is None or balance < 1:
                flash('Deposit amount must be greater than 0.', category='error')
            else:
                existing_account.balance = existing_account.balance + balance
                db.session.commit()
                flash('Amount deposited.', category='success')
                return redirect(url_for('views.view_accounts'))
        else:
            flash('That account does not exist', category='error')

    return render_template("deposit.html", user=current_user)


@auth.route('/withdraw', methods=['GET', 'POST'])
@login_required
def withdraw():
    
    if request.method == 'POST':
        id = request.form.get('id')
        balance = request.form.get('balance')

        balance = int(balance)
        existing_account = Account.query.get(id)

        if existing_account and existing_account.user_id == current_user.id:
            if balance is None or balance < 1:
                flash('Deposit amount must be greater than 0.', category='error')
            elif balance > existing_account.balance:
                flash('Withdrawal amount is greater than account balance.', category='error')
            else:
                existing_account.balance = existing_account.balance - balance
                db.session.commit()
                flash('Amount withdrawn.', category='success')
                return redirect(url_for('views.view_accounts'))
        else:
            flash('That account does not exist', category='error')
    
    
    return render_template("withdraw.html", user=current_user)