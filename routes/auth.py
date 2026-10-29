import random
import string
from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from models import db
from models.user import User, PlayerStats
from config import Config

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if 'user_id' in session and not session.get('is_guest'):
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip().lower()
        password = request.form.get('password', '')
        confirm_password = request.form.get('confirm_password', '')
        avatar = request.form.get('avatar', 'cyber_ninja')

        if not username or len(username) < 3 or len(username) > 20:
            flash('Username must be between 3 and 20 characters.', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        if not username.replace('_', '').isalnum():
            flash('Username can only contain alphanumeric characters and underscores.', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        if len(password) < 6:
            flash('Password must be at least 6 characters long.', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        if password != confirm_password:
            flash('Passwords do not match.', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        if User.query.filter_by(username=username).first():
            flash('Username is already taken. Choose another battle tag!', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        if email and User.query.filter_by(email=email).first():
            flash('Email is already registered.', 'danger')
            return render_template('register.html', avatars=Config.AVATARS)

        user = User(
            username=username,
            email=email if email else None,
            avatar=avatar if avatar in Config.AVATARS else 'cyber_ninja',
            is_guest=False
        )
        user.set_password(password)
        db.session.add(user)
        db.session.flush()

        # Initialize stats
        stats = PlayerStats(user_id=user.id)
        db.session.add(stats)
        db.session.commit()

        # Set session
        session['user_id'] = user.id
        session['username'] = user.username
        session['avatar'] = user.avatar
        session['is_guest'] = False
        session['is_admin'] = user.is_admin

        flash(f'Welcome to Quiz Clash, {user.username}! Your battle station is ready.', 'success')
        return redirect(url_for('dashboard.dashboard_view'))

    return render_template('register.html', avatars=Config.AVATARS)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session and not session.get('is_guest'):
        return redirect(url_for('dashboard.dashboard_view'))

    if request.method == 'POST':
        login_id = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter((User.username == login_id) | (User.email == login_id.lower())).first()
        if not user or not user.check_password(password):
            flash('Invalid username/email or password.', 'danger')
            return render_template('login.html')

        session['user_id'] = user.id
        session['username'] = user.username
        session['avatar'] = user.avatar
        session['is_guest'] = user.is_guest
        session['is_admin'] = user.is_admin

        flash(f'Welcome back, Commander {user.username}!', 'success')
        return redirect(url_for('dashboard.dashboard_view'))

    return render_template('login.html')


@auth_bp.route('/guest', methods=['GET', 'POST'])
def guest_login():
    """Create a temporary guest user account for instant demonstration"""
    random_suffix = ''.join(random.choices(string.digits, k=4))
    guest_username = f"Guest_{random_suffix}"
    guest_avatar = random.choice(Config.AVATARS)

    guest_user = User(
        username=guest_username,
        avatar=guest_avatar,
        is_guest=True
    )
    guest_user.set_password('guest_pass_' + random_suffix)
    db.session.add(guest_user)
    db.session.flush()

    stats = PlayerStats(user_id=guest_user.id)
    db.session.add(stats)
    db.session.commit()

    session['user_id'] = guest_user.id
    session['username'] = guest_user.username
    session['avatar'] = guest_user.avatar
    session['is_guest'] = True
    session['is_admin'] = False

    flash(f'Entered as Guest operative: {guest_username}. Your session is active!', 'info')
    return redirect(url_for('dashboard.dashboard_view'))


@auth_bp.route('/logout')
def logout():
    session.clear()
    flash('You have logged out of the arena. Come back soon!', 'info')
    return redirect(url_for('main.index'))
