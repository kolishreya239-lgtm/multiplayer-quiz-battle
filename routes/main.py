from flask import Blueprint, render_template
from models import db
from models.user import User, PlayerStats
from models.question import Category, Question
from models.game import MatchHistory

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    # Fetch real live metrics from SQLite
    total_players = User.query.filter_by(is_guest=False).count()
    total_battles = MatchHistory.query.count()
    total_categories = Category.query.count()
    total_questions = Question.query.count()

    # Top 3 players preview for landing page
    top_players = (
        db.session.query(User, PlayerStats)
        .join(PlayerStats, User.id == PlayerStats.user_id)
        .filter(User.is_guest == False)
        .order_by(PlayerStats.total_score.desc())
        .limit(3)
        .all()
    )

    categories = Category.query.all()

    return render_template(
        'index.html',
        total_players=total_players,
        total_battles=total_battles,
        total_categories=total_categories,
        total_questions=total_questions,
        top_players=top_players,
        categories=categories
    )


@main_bp.route('/how-to-play')
def how_to_play():
    return render_template('how_to_play.html')


@main_bp.route('/rules')
def rules():
    return render_template('rules.html')
