from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from app import db
from app.models import User

bp = Blueprint('auth', __name__, url_prefix='/auth')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('events.list_events')) # Redirect to main page

    if request.method == 'POST':
        country_code = (request.form.get('country_code') or '').strip()
        telephone = (request.form.get('telephone') or '').strip()
        name = request.form.get('name')

        if not telephone or not name or not country_code:
            flash('Name, Country Code, and Telephone are required.')
            return redirect(url_for('auth.login'))

        if country_code.startswith('+'):
            country_code = country_code[1:]
        full_telephone = f"{country_code}{telephone}"

        user = User.query.filter_by(telephone=full_telephone).first()
        
        if user:
            # Existing user
            # Optionally update name if different? User story implies simple login.
            # Let's keep it simple: just login.
            login_user(user)
        else:
            # Create new user
            user = User(name=name, telephone=full_telephone)
            db.session.add(user)
            db.session.commit()
            login_user(user)
            flash('Account created successfully!')

        next_page = request.args.get('next')
        return redirect(next_page or url_for('events.list_events'))

    return render_template('auth/login.html')

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))

@bp.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    if request.method == 'POST':
        email = request.form.get('email')
        name = request.form.get('name') # Allow name update too
        
        # Validations could go here
        
        current_user.email = email
        current_user.name = name
        try:
            db.session.commit()
            flash('Profile updated.')
        except:
            db.session.rollback()
            flash('Error updating profile. Email might be in use.')

    return render_template('auth/profile.html')
