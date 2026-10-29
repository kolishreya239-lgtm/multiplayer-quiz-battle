import functools
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, abort
from models import db
from models.user import User
from models.question import Question, Category
from models.game import MatchHistory

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

def admin_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Admin login required.', 'danger')
            return redirect(url_for('auth.login'))
        user = db.session.get(User, session['user_id'])
        if not user or not user.is_admin:
            flash('Access denied. Administrator privileges required.', 'danger')
            return redirect(url_for('dashboard.dashboard_view'))
        return view(**kwargs)
    return wrapped_view


@admin_bp.route('/', strict_slashes=False)
@admin_required
def admin_panel():
    total_users = User.query.count()
    total_questions = Question.query.count()
    total_categories = Category.query.count()
    total_battles = MatchHistory.query.count()

    categories = Category.query.all()

    # Filter questions
    category_id = request.args.get('category_id')
    difficulty = request.args.get('difficulty')
    search_q = request.args.get('q', '').strip()

    q_query = Question.query
    if category_id and category_id != 'all':
        q_query = q_query.filter_by(category_id=int(category_id))
    if difficulty and difficulty != 'all':
        q_query = q_query.filter_by(difficulty=difficulty)
    if search_q:
        q_query = q_query.filter(Question.question_text.ilike(f'%{search_q}%'))

    questions = q_query.order_by(Question.id.desc()).all()

    recent_battles = MatchHistory.query.order_by(MatchHistory.played_at.desc()).limit(8).all()

    return render_template(
        'admin.html',
        total_users=total_users,
        total_questions=total_questions,
        total_categories=total_categories,
        total_battles=total_battles,
        categories=categories,
        questions=questions,
        recent_battles=recent_battles,
        selected_category=category_id,
        selected_difficulty=difficulty,
        search_q=search_q
    )


@admin_bp.route('/question/add', methods=['POST'])
@admin_required
def add_question():
    category_id = int(request.form.get('category_id'))
    difficulty = request.form.get('difficulty', 'medium')
    question_text = request.form.get('question_text', '').strip()
    option_a = request.form.get('option_a', '').strip()
    option_b = request.form.get('option_b', '').strip()
    option_c = request.form.get('option_c', '').strip()
    option_d = request.form.get('option_d', '').strip()
    correct_option = request.form.get('correct_option', 'A').upper()
    explanation = request.form.get('explanation', '').strip()

    if not (question_text and option_a and option_b and option_c and option_d):
        flash('All question fields and options are required.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    q = Question(
        category_id=category_id,
        difficulty=difficulty,
        question_text=question_text,
        option_a=option_a,
        option_b=option_b,
        option_c=option_c,
        option_d=option_d,
        correct_option=correct_option,
        explanation=explanation
    )
    db.session.add(q)
    db.session.commit()
    flash('Question successfully created and added to the battle pool!', 'success')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/question/delete/<int:question_id>', methods=['POST'])
@admin_required
def delete_question(question_id):
    q = db.session.get(Question, question_id)
    if q:
        db.session.delete(q)
        db.session.commit()
        flash('Question deleted successfully.', 'info')
    return redirect(url_for('admin.admin_panel'))


@admin_bp.route('/category/add', methods=['POST'])
@admin_required
def add_category():
    name = request.form.get('name', '').strip()
    slug = name.lower().replace(' ', '-').replace('&', 'and')
    description = request.form.get('description', '').strip()
    color_hex = request.form.get('color_hex', '#00E5FF')
    icon_name = request.form.get('icon_name', 'zap')

    if not name:
        flash('Category name is required.', 'danger')
        return redirect(url_for('admin.admin_panel'))

    if Category.query.filter_by(name=name).first():
        flash('Category already exists.', 'warning')
        return redirect(url_for('admin.admin_panel'))

    cat = Category(name=name, slug=slug, description=description, color_hex=color_hex, icon_name=icon_name)
    db.session.add(cat)
    db.session.commit()
    flash(f'Category "{name}" created successfully.', 'success')
    return redirect(url_for('admin.admin_panel'))
