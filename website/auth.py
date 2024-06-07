from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user


auth = Blueprint('auth', __name__)

def create_admin_user():
    """Creates an initial admin user with a default password."""   
    email="admin@company.com"
    admin_user = User.query.filter_by(email=email).first()
    # Check if admin user already exists
    if not admin_user:
      admin_user = User(email=email, first_name="admin", password=generate_password_hash( "123", method='pbkdf2:sha256'), is_admin=True)
      db.session.add(admin_user)
      db.session.commit()
      print("Created admin user!")


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()
        if user:
            if check_password_hash(user.password, password):
                flash('Logged in successfully!', category='success')
                login_user(user, remember=True)
                return redirect(url_for('views.home'))
            else:
                flash('Incorrect password, try again.', category='error')
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
        first_name = request.form.get('firstName')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')

        user = User.query.filter_by(email=email).first()
        if user:
            flash('Email already exists.', category='error')
        elif len(email) < 4:
            flash('Email must be greater than 3 characters.', category='error')
        elif len(first_name) < 2:
            flash('First name must be greater than 1 character.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 3:
            flash('Password must be at least 3 characters.', category='error')
        else:
            new_user = User(email=email, first_name=first_name, password=generate_password_hash(
                password1, method='pbkdf2:sha256'))
            db.session.add(new_user)
            db.session.commit()
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.home'))

    return render_template("sign_up.html", user=current_user)

@auth.route('/admin/manage_users', methods=['POST'])
@login_required
def manage_users():
  if current_user.is_authenticated and current_user.is_admin:
    users = User.query.filter(User.id != current_user.id).all()

    selected_user_id = request.form.get('user_id')  # Assuming you submit the user ID in the POST request
    selected_action = request.form.get('action')
    new_password = request.form.get('user_password')  # Assuming you submit the new password in the POST request

    if selected_action == 'delete':
      # Validate user ID and perform secure deletion logic
      user = User.query.get(selected_user_id)
      if user:
        db.session.delete(user)
        db.session.commit()
        flash('User deleted successfully!', 'success')
      else:
        flash('Invalid user ID for deletion!', 'error')
    elif selected_action == 'change_password':
      # Validate user ID and new password, then update password
      user = User.query.get(selected_user_id)
      if user and new_password:
        # Update user password securely (hashing)
        user.password = generate_password_hash(new_password, method='pbkdf2:sha256')
        db.session.commit()
      else:
        flash('Invalid user ID or password!', 'error')
    users = User.query.filter(User.id != current_user.id).all()
    return render_template('admin.html', users=users, user=current_user)  # Re-render with flash messages