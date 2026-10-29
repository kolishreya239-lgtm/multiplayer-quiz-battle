from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db
from models.user import User, PlayerStats, Achievement, UserAchievement
from models.game import MatchHistory, MatchParticipant
from routes.dashboard import login_required
from config import Config

profile_bp = Blueprint('profile', __name__)

@profile_bp.route('/profile')
@profile_bp.route('/profile/<username>')
@login_required
def profile_view(username=None):
    current_uid = session.get('user_id')
    
    if username:
        user = User.query.filter_by(username=username).first()
        if not user:
            flash(f'Player "{username}" was not found.', 'danger')
            return redirect(url_for('dashboard.dashboard_view'))
    else:
        user = db.session.get(User, current_uid)
        if not user:
            session.clear()
            return redirect(url_for('auth.login'))

    is_own_profile = (user.id == current_uid)

    stats = user.stats
    if not stats:
        stats = PlayerStats(user_id=user.id)
        db.session.add(stats)
        db.session.commit()

    # Recent matches
    matches = (
        db.session.query(MatchParticipant, MatchHistory)
        .join(MatchHistory, MatchParticipant.match_id == MatchHistory.id)
        .filter(MatchParticipant.user_id == user.id)
        .order_by(MatchHistory.played_at.desc())
        .limit(10)
        .all()
    )

    # Achievements
    all_achievements = Achievement.query.all()
    unlocked_map = {
        ua.achievement_id: ua.unlocked_at
        for ua in UserAchievement.query.filter_by(user_id=user.id).all()
    }

    achievements_data = []
    for ach in all_achievements:
        achievements_data.append({
            'achievement': ach,
            'is_unlocked': ach.id in unlocked_map,
            'unlocked_at': unlocked_map.get(ach.id)
        })

    return render_template(
        'profile.html',
        profile_user=user,
        stats=stats,
        matches=matches,
        achievements=achievements_data,
        is_own_profile=is_own_profile,
        available_avatars=Config.AVATARS
    )


@profile_bp.route('/profile/update-avatar', methods=['POST'])
@login_required
def update_avatar():
    new_avatar = request.form.get('avatar')
    if new_avatar in Config.AVATARS:
        user = db.session.get(User, session['user_id'])
        if user:
            user.avatar = new_avatar
            db.session.commit()
            session['avatar'] = new_avatar
            flash('Avatar updated successfully!', 'success')
    return redirect(url_for('profile.profile_view'))
