from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required,  current_user
from .models import Account
from . import db
import json

views = Blueprint('views', __name__)

@views.route('/', methods=['GET'])
@login_required
def home():
    return render_template("home.html", user=current_user)

@views.route('/view', methods=['GET', 'POST'])
@login_required
def view_accounts():
    return render_template("view_accounts.html", user=current_user)

@views.route('/delete-account', methods=['POST'])
def delete_account():
    account = json.loads(request.data)
    accountId = account['accountId']
    account = Account.query.get(accountId)
    if account:
        if account.user_id == current_user.id:
            db.session.delete(account)
            db.session.commit()

    return jsonify({})