from flask import Blueprint, render_template, request, session
from models import db
from models.user import User, PlayerStats

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/leaderboard')
def leaderboard_view():
    sort_by = request.args.get('sort', 'points')  # 'points' or 'wins'
    search_query = request.args.get('q', '').strip()

    query = (
        db.session.query(User, PlayerStats)
        .join(PlayerStats, User.id == PlayerStats.user_id)
        .filter(User.is_guest == False)
    )

    if search_query:
        query = query.filter(User.username.ilike(f'%{search_query}%'))

    if sort_by == 'wins':
        query = query.order_by(PlayerStats.wins.desc(), PlayerStats.total_score.desc())
    else:
        query = query.order_by(PlayerStats.total_score.desc(), PlayerStats.wins.desc())

    players = query.all()

    # Determine podium (top 3)
    podium = players[:3]
    rankings = players

    # Determine current user's rank
    current_user_rank = None
    current_user_id = session.get('user_id')
    if current_user_id:
        for index, (u, s) in enumerate(players, start=1):
            if u.id == current_user_id:
                current_user_rank = index
                break

    return render_template(
        'leaderboard.html',
        podium=podium,
        rankings=rankings,
        sort_by=sort_by,
        search_query=search_query,
        current_user_rank=current_user_rank
    )
