import functools
import random
from datetime import datetime, date
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify
from models import db
from models.user import User, PlayerStats
from models.question import Category, Question
from models.game import MatchHistory, MatchParticipant, DailyChallengeRecord
from game.room_manager import room_manager, PlayerState
from config import Config

dashboard_bp = Blueprint('dashboard', __name__)

def login_required(view):
    @functools.wraps(view)
    def wrapped_view(**kwargs):
        if 'user_id' not in session:
            flash('Please log in or continue as Guest to access the battle arena.', 'warning')
            return redirect(url_for('auth.login'))
        return view(**kwargs)
    return wrapped_view


@dashboard_bp.route('/dashboard')
@login_required
def dashboard_view():
    user = db.session.get(User, session['user_id'])
    if not user:
        session.clear()
        return redirect(url_for('auth.login'))

    stats = user.stats
    if not stats:
        stats = PlayerStats(user_id=user.id)
        db.session.add(stats)
        db.session.commit()

    # Active public rooms
    open_rooms = room_manager.get_open_rooms()
    categories = Category.query.all()

    # Player's recent matches
    recent_matches = (
        db.session.query(MatchParticipant, MatchHistory)
        .join(MatchHistory, MatchParticipant.match_id == MatchHistory.id)
        .filter(MatchParticipant.user_id == user.id)
        .order_by(MatchHistory.played_at.desc())
        .limit(5)
        .all()
    )

    # Check daily challenge status for today
    today_str = date.today().strftime('%Y-%m-%d')
    daily_record = DailyChallengeRecord.query.filter_by(user_id=user.id, challenge_date=today_str).first()

    return render_template(
        'dashboard.html',
        user=user,
        stats=stats,
        open_rooms=open_rooms,
        categories=categories,
        recent_matches=recent_matches,
        daily_record=daily_record,
        today_str=today_str
    )


@dashboard_bp.route('/create-room', methods=['POST'])
@login_required
def create_room():
    user = db.session.get(User, session['user_id'])
    game_mode = request.form.get('game_mode', 'pvp')
    category_id = request.form.get('category_id')
    difficulty = request.form.get('difficulty', 'all')
    question_count = int(request.form.get('question_count', Config.DEFAULT_QUESTION_COUNT))
    question_time = int(request.form.get('question_time', Config.DEFAULT_QUESTION_TIME))

    # Create host player state
    # We assign a temporary sid placeholder; it will update once client connects socket
    temp_sid = f"temp_{user.id}_{random.randint(1000, 9999)}"
    host_player = PlayerState(
        sid=temp_sid,
        user_id=user.id,
        username=user.username,
        avatar=user.avatar,
        is_guest=user.is_guest
    )

    room = room_manager.create_room(host_sid=temp_sid, host_player=host_player, game_mode=game_mode)
    
    # Configure room settings
    if category_id and category_id != 'all':
        try:
            cat = db.session.get(Category, int(category_id))
            if cat:
                room.category_id = cat.id
                room.category_name = cat.name
        except ValueError:
            pass

    room.difficulty = difficulty
    room.question_count = max(3, min(15, question_count))
    room.question_time = max(8, min(30, question_time))

    flash(f'Battle Room {room.code} created! Share the code with your opponent.', 'success')
    return redirect(url_for('dashboard.lobby_view', room_code=room.code))


@dashboard_bp.route('/join-room', methods=['POST'])
@login_required
def join_room_post():
    room_code = request.form.get('room_code', '').upper().strip()
    if not room_code:
        flash('Please enter a room code.', 'danger')
        return redirect(url_for('dashboard.dashboard_view'))

    room = room_manager.get_room(room_code)
    if not room:
        flash(f'Room "{room_code}" was not found or has expired.', 'danger')
        return redirect(url_for('dashboard.dashboard_view'))

    if room.state != 'waiting':
        flash('This room is already in battle!', 'warning')
        return redirect(url_for('dashboard.dashboard_view'))

    if len(room.players) >= 4:
        flash('Room is already at full capacity (4 players).', 'warning')
        return redirect(url_for('dashboard.dashboard_view'))

    return redirect(url_for('dashboard.lobby_view', room_code=room.code))


@dashboard_bp.route('/lobby/<room_code>')
@login_required
def lobby_view(room_code):
    room_code = room_code.upper().strip()
    room = room_manager.get_room(room_code)
    if not room:
        flash(f'Room "{room_code}" no longer exists.', 'danger')
        return redirect(url_for('dashboard.dashboard_view'))

    categories = Category.query.all()
    user = db.session.get(User, session['user_id'])
    return render_template('lobby.html', room=room, categories=categories, user=user)


@dashboard_bp.route('/battle/<room_code>')
@login_required
def battle_view(room_code):
    room_code = room_code.upper().strip()
    room = room_manager.get_room(room_code)
    if not room:
        flash(f'Room "{room_code}" does not exist.', 'danger')
        return redirect(url_for('dashboard.dashboard_view'))

    user = db.session.get(User, session['user_id'])
    return render_template('battle.html', room=room, user=user)


# Solo Practice Mode
@dashboard_bp.route('/practice')
@login_required
def practice_view():
    categories = Category.query.all()
    selected_cat = request.args.get('category', 'all')
    difficulty = request.args.get('difficulty', 'all')
    user = db.session.get(User, session['user_id'])

    return render_template(
        'practice.html',
        categories=categories,
        selected_cat=selected_cat,
        difficulty=difficulty,
        user=user
    )


@dashboard_bp.route('/api/practice/questions')
@login_required
def api_practice_questions():
    category_id = request.args.get('category_id')
    difficulty = request.args.get('difficulty', 'all')
    count = min(15, max(3, int(request.args.get('count', 5))))

    query = Question.query
    if category_id and category_id != 'all':
        query = query.filter_by(category_id=int(category_id))
    if difficulty and difficulty != 'all':
        query = query.filter_by(difficulty=difficulty)

    all_q = query.all()
    if not all_q:
        all_q = Question.query.all()

    sampled = random.sample(all_q, min(count, len(all_q)))
    return jsonify([q.to_dict(include_answer=True) for q in sampled])


# Daily Challenge Mode
@dashboard_bp.route('/daily-challenge')
@login_required
def daily_challenge():
    user = db.session.get(User, session['user_id'])
    today_str = date.today().strftime('%Y-%m-%d')
    record = DailyChallengeRecord.query.filter_by(user_id=user.id, challenge_date=today_str).first()

    return render_template('daily_challenge.html', user=user, today_str=today_str, record=record)


@dashboard_bp.route('/api/daily-challenge/questions')
@login_required
def api_daily_questions():
    today_str = date.today().strftime('%Y-%m-%d')
    # Use deterministic seed based on today's date so all players get the exact same daily questions!
    date_seed = int(today_str.replace('-', ''))
    rnd = random.Random(date_seed)

    all_q = Question.query.all()
    if not all_q:
        return jsonify([])

    # Pick 5 questions deterministically
    sampled = rnd.sample(all_q, min(5, len(all_q)))
    # Return without correct answer initially; client submits answers to be validated
    return jsonify([q.to_dict(include_answer=False) for q in sampled])


@dashboard_bp.route('/api/daily-challenge/submit', methods=['POST'])
@login_required
def api_daily_submit():
    user = db.session.get(User, session['user_id'])
    today_str = date.today().strftime('%Y-%m-%d')

    # Prevent multiple submissions for official daily challenge score
    existing = DailyChallengeRecord.query.filter_by(user_id=user.id, challenge_date=today_str).first()
    if existing:
        return jsonify({'error': 'You have already submitted today\'s official Daily Challenge!', 'record': existing.to_dict()}), 400

    data = request.get_json() or {}
    answers = data.get('answers', {})  # { question_id: 'A', ... }
    times = data.get('times', {})      # { question_id: 3.4, ... }

    total_score = 0
    correct_count = 0
    breakdown = []

    for q_id_str, selected_option in answers.items():
        try:
            q_id = int(q_id_str)
            question = db.session.get(Question, q_id)
            if not question:
                continue

            time_taken = float(times.get(q_id_str, 15.0))
            is_correct = (selected_option.upper() == question.correct_option.upper())

            pts = 0
            if is_correct:
                correct_count += 1
                base = Config.BASE_POINTS_CORRECT
                speed_bonus = int(round(max(0, (15 - time_taken) / 15) * Config.MAX_SPEED_BONUS))
                pts = base + speed_bonus
                total_score += pts

            breakdown.append({
                'question_id': q_id,
                'question_text': question.question_text,
                'user_option': selected_option,
                'correct_option': question.correct_option,
                'is_correct': is_correct,
                'points': pts,
                'explanation': question.explanation
            })
        except Exception:
            continue

    record = DailyChallengeRecord(
        user_id=user.id,
        challenge_date=today_str,
        score=total_score,
        correct_count=correct_count,
        total_questions=len(answers)
    )
    db.session.add(record)

    # Also update player's total stats
    if user.stats:
        user.stats.total_score += total_score
        user.stats.total_correct += correct_count
        user.stats.total_answered += len(answers)

    db.session.commit()

    return jsonify({
        'success': True,
        'record': record.to_dict(),
        'breakdown': breakdown
    })
