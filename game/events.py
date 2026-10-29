import time
import random
from flask import request, session
from flask_socketio import emit, join_room, leave_room
from models import db
from models.user import User, PlayerStats, Achievement, UserAchievement
from models.question import Question, Category
from models.game import MatchHistory, MatchParticipant
from game.room_manager import room_manager, PlayerState, Room
from game.scoring import calculate_score, compute_final_ranks
from config import Config

def register_socket_events(socketio, app):

    @socketio.on('connect')
    def handle_connect():
        pass

    @socketio.on('disconnect')
    def handle_disconnect():
        sid = request.sid
        room_manager.remove_from_quick_queue(sid)
        room = room_manager.get_room_by_sid(sid)
        if room:
            player = room.get_player(sid)
            if player:
                player.connected = False
            
            # If still in waiting lobby, remove player
            if room.state == 'waiting':
                room_manager.leave_room(sid)
                if len(room.players) > 0:
                    emit('lobby_updated', room.to_dict(), room=room.code)
                    emit('player_left', {'username': player.username if player else 'A player'}, room=room.code)
            else:
                # In game: check if all remaining connected players have answered
                emit('player_disconnected', {'username': player.username if player else 'Player', 'sid': sid}, room=room.code)
                if room.all_active_players_answered() and room.state == 'in_progress':
                    # All active answered -> reveal
                    socketio.start_background_task(reveal_round_results, room.code)

    @socketio.on('join_lobby')
    def handle_join_lobby(data):
        room_code = data.get('room_code', '').upper().strip()
        user_id = session.get('user_id')
        username = session.get('username')
        avatar = session.get('avatar', 'cyber_ninja')
        is_guest = session.get('is_guest', False)

        if not user_id or not username:
            emit('error_message', {'message': 'Session expired. Please log in or continue as guest.'})
            return

        room = room_manager.get_room(room_code)
        if not room:
            emit('error_message', {'message': f'Room "{room_code}" not found. Please check the code.'})
            return

        if room.state != 'waiting' and room.get_player_by_user_id(user_id) is None:
            emit('error_message', {'message': 'This battle is already in progress!'})
            return

        player = PlayerState(
            sid=request.sid,
            user_id=user_id,
            username=username,
            avatar=avatar,
            is_guest=is_guest
        )
        
        joined_room = room_manager.join_room(room_code, player)
        if not joined_room:
            emit('error_message', {'message': 'Room is full or cannot be joined.'})
            return

        join_room(room_code)
        emit('lobby_updated', joined_room.to_dict(), room=room_code)
        emit('player_joined', {'username': username}, room=room_code)

    @socketio.on('toggle_ready')
    def handle_toggle_ready():
        sid = request.sid
        room = room_manager.get_room_by_sid(sid)
        if not room or room.state != 'waiting':
            return

        player = room.get_player(sid)
        if player:
            player.is_ready = not player.is_ready
            emit('lobby_updated', room.to_dict(), room=room.code)

    @socketio.on('update_room_settings')
    def handle_update_settings(data):
        sid = request.sid
        room = room_manager.get_room_by_sid(sid)
        if not room or room.state != 'waiting':
            return

        # Only host can update settings
        if room.host_sid != sid:
            emit('error_message', {'message': 'Only the host can modify room settings.'})
            return

        cat_id = data.get('category_id')
        if cat_id is not None:
            if cat_id == '' or cat_id == 'all':
                room.category_id = None
                room.category_name = 'All Categories'
            else:
                try:
                    cat_id_int = int(cat_id)
                    with app.app_context():
                        cat = db.session.get(Category, cat_id_int)
                        if cat:
                            room.category_id = cat.id
                            room.category_name = cat.name
                except Exception:
                    pass

        difficulty = data.get('difficulty', 'all').lower()
        if difficulty in ['all', 'easy', 'medium', 'hard']:
            room.difficulty = difficulty

        q_count = data.get('question_count')
        if q_count:
            try:
                room.question_count = max(3, min(15, int(q_count)))
            except ValueError:
                pass

        q_time = data.get('question_time')
        if q_time:
            try:
                room.question_time = max(8, min(30, int(q_time)))
            except ValueError:
                pass

        emit('lobby_updated', room.to_dict(), room=room.code)

    @socketio.on('start_game')
    def handle_start_game():
        sid = request.sid
        room = room_manager.get_room_by_sid(sid)
        if not room or room.state != 'waiting':
            return

        if room.host_sid != sid:
            emit('error_message', {'message': 'Only the host can start the battle.'})
            return

        # Validate minimum players
        if room.game_mode == 'pvp' and len(room.players) < 2:
            emit('error_message', {'message': 'At least 2 players are required for a Multiplayer Battle! (Invite a friend or open a second browser window).'})
            return

        # Check all players ready
        if room.game_mode == 'pvp' and not room.all_players_ready():
            emit('error_message', {'message': 'All players must be Ready before the battle can begin.'})
            return

        # Fetch questions from database
        with app.app_context():
            query = Question.query
            if room.category_id:
                query = query.filter_by(category_id=room.category_id)
            if room.difficulty != 'all':
                query = query.filter_by(difficulty=room.difficulty)
            
            all_questions = query.all()
            if not all_questions:
                # Fallback to any questions
                all_questions = Question.query.all()

            if not all_questions:
                emit('error_message', {'message': 'No questions found in database. Please seed questions.'})
                return

            # Random sample up to question_count
            sample_count = min(room.question_count, len(all_questions))
            selected = random.sample(all_questions, sample_count)
            room.questions = [q.to_dict(include_answer=True) for q in selected]

        room.state = 'in_progress'
        room.current_question_index = -1
        for p in room.players.values():
            p.reset_for_game()

        # Emit game_starting countdown
        emit('game_starting', {
            'countdown': 3,
            'total_questions': len(room.questions),
            'room_code': room.code
        }, room=room.code)

        def delayed_start():
            time.sleep(3)
            deliver_next_question(room.code)

        socketio.start_background_task(delayed_start)

    def deliver_next_question(room_code: str):
        room = room_manager.get_room(room_code)
        if not room or room.state != 'in_progress':
            return

        room.current_question_index += 1
        if room.current_question_index >= len(room.questions):
            finish_game(room_code)
            return

        current_q = room.get_current_question()
        if not current_q:
            finish_game(room_code)
            return

        room.reset_answers_for_round()
        room.question_start_time = time.time()

        # Send public question data (WITHOUT answer/explanation)
        public_q = {
            'question_number': room.current_question_index + 1,
            'total_questions': len(room.questions),
            'category_name': current_q.get('category_name', room.category_name),
            'difficulty': current_q.get('difficulty', 'medium'),
            'question_text': current_q['question_text'],
            'options': current_q['options'],
            'question_time': room.question_time,
            'players': [p.to_dict() for p in room.players.values()]
        }

        socketio.emit('new_question', public_q, room=room_code)

        # Start timer watcher
        current_idx = room.current_question_index

        def timer_worker():
            total_time = room.question_time
            time.sleep(total_time)
            # If still on the same question, reveal results
            r = room_manager.get_room(room_code)
            if r and r.state == 'in_progress' and r.current_question_index == current_idx:
                reveal_round_results(room_code)

        socketio.start_background_task(timer_worker)

    @socketio.on('submit_answer')
    def handle_submit_answer(data):
        sid = request.sid
        room = room_manager.get_room_by_sid(sid)
        if not room or room.state != 'in_progress':
            return

        player = room.get_player(sid)
        if not player or player.current_answer is not None:
            # Already answered this round or invalid
            return

        current_q = room.get_current_question()
        if not current_q:
            return

        selected_option = data.get('option', '').upper().strip()
        elapsed_seconds = max(0.1, time.time() - room.question_start_time)
        
        # Check if answered past timer limit (with small grace margin)
        if elapsed_seconds > (room.question_time + 1.5):
            return

        correct_option = current_q['correct_option'].upper()
        is_correct = (selected_option == correct_option)

        score_result = calculate_score(
            is_correct=is_correct,
            time_taken=elapsed_seconds,
            question_time=room.question_time,
            current_streak=player.streak
        )

        player.score += score_result['points']
        player.streak = score_result['new_streak']
        player.max_streak = max(player.max_streak, player.streak)
        player.total_answered += 1
        player.total_time_taken += elapsed_seconds
        if is_correct:
            player.correct_count += 1

        player.current_answer = {
            'option': selected_option,
            'time_taken': round(elapsed_seconds, 2),
            'points_earned': score_result['points'],
            'base': score_result['base'],
            'speed_bonus': score_result['speed_bonus'],
            'streak_bonus': score_result['streak_bonus'],
            'is_correct': is_correct
        }

        # Send immediate individual acknowledgement to this player
        emit('answer_acknowledged', {
            'option': selected_option,
            'time_taken': round(elapsed_seconds, 2)
        })

        # Broadcast update to room so everyone sees player has answered (without revealing the answer yet!)
        emit('player_submitted', {
            'sid': player.sid,
            'username': player.username,
            'has_answered': True,
            'all_answered': room.all_active_players_answered()
        }, room=room.code)

        # If all active players have answered, trigger reveal immediately!
        if room.all_active_players_answered():
            socketio.start_background_task(reveal_round_results, room.code)

    def reveal_round_results(room_code: str):
        room = room_manager.get_room(room_code)
        if not room or room.state != 'in_progress':
            return

        current_q = room.get_current_question()
        if not current_q:
            return

        # Mark unanswered players as 0
        for p in room.players.values():
            if p.connected and p.current_answer is None:
                p.current_answer = {
                    'option': None,
                    'time_taken': room.question_time,
                    'points_earned': 0,
                    'base': 0,
                    'speed_bonus': 0,
                    'streak_bonus': 0,
                    'is_correct': False
                }
                p.streak = 0
                p.total_answered += 1
                p.total_time_taken += room.question_time

        # Compile round breakdown
        results_data = {
            'correct_option': current_q['correct_option'],
            'explanation': current_q.get('explanation', ''),
            'intermission_time': Config.INTERMISSION_TIME,
            'players': [
                {
                    'sid': p.sid,
                    'username': p.username,
                    'avatar': p.avatar,
                    'score': p.score,
                    'streak': p.streak,
                    'max_streak': p.max_streak,
                    'answer': p.current_answer
                }
                for p in room.players.values()
            ]
        }

        socketio.emit('round_revealed', results_data, room=room_code)

        def intermission_worker():
            time.sleep(Config.INTERMISSION_TIME)
            r = room_manager.get_room(room_code)
            if r and r.state == 'in_progress':
                deliver_next_question(room_code)

        socketio.start_background_task(intermission_worker)

    def finish_game(room_code: str):
        room = room_manager.get_room(room_code)
        if not room:
            return

        room.state = 'finished'
        ranked_players = compute_final_ranks([p.to_dict() for p in room.players.values()])
        
        is_draw = False
        winner_user_id = None
        winner_username = 'None'

        if len(ranked_players) > 0:
            top_player = ranked_players[0]
            if len(ranked_players) > 1 and ranked_players[0]['score'] == ranked_players[1]['score']:
                is_draw = True
            else:
                winner_user_id = top_player['user_id']
                winner_username = top_player['username']

        # Persist match & player stats in SQLite
        newly_unlocked_achievements = {}
        with app.app_context():
            try:
                # Save MatchHistory
                match_record = MatchHistory(
                    room_code=room.code,
                    game_mode=room.game_mode,
                    category_id=room.category_id,
                    difficulty=room.difficulty,
                    total_questions=len(room.questions),
                    winner_id=winner_user_id if not is_draw else None,
                    is_draw=is_draw
                )
                db.session.add(match_record)
                db.session.flush()

                # Save participants & update stats
                for p_data in ranked_players:
                    uid = p_data['user_id']
                    user = db.session.get(User, uid)
                    if not user:
                        continue

                    # MatchParticipant
                    participant = MatchParticipant(
                        match_id=match_record.id,
                        user_id=uid,
                        final_score=p_data['score'],
                        rank=p_data['rank'],
                        correct_count=p_data['correct_count'],
                        total_answered=p_data['total_answered'],
                        avg_response_time=p_data['avg_response_time']
                    )
                    db.session.add(participant)

                    # Update PlayerStats
                    stats = user.stats
                    if not stats:
                        stats = PlayerStats(user_id=uid)
                        db.session.add(stats)

                    stats.total_games += 1
                    stats.total_score += p_data['score']
                    stats.highest_score = max(stats.highest_score, p_data['score'])
                    stats.total_correct += p_data['correct_count']
                    stats.total_answered += p_data['total_answered']
                    stats.max_streak = max(stats.max_streak, p_data['max_streak'])

                    if not is_draw and uid == winner_user_id:
                        stats.wins += 1
                        stats.current_streak += 1
                    elif is_draw:
                        stats.draws += 1
                    else:
                        stats.losses += 1
                        stats.current_streak = 0

                    # Check achievements
                    unlocked = check_and_award_achievements(user, stats, p_data, room)
                    if unlocked:
                        newly_unlocked_achievements[p_data['sid']] = unlocked

                db.session.commit()
            except Exception as e:
                db.session.rollback()
                print(f"[Error saving match results]: {e}")

        final_data = {
            'room_code': room.code,
            'is_draw': is_draw,
            'winner_id': winner_user_id,
            'winner_username': winner_username,
            'ranked_players': ranked_players,
            'unlocked_achievements': newly_unlocked_achievements
        }

        socketio.emit('game_over', final_data, room=room_code)

    def check_and_award_achievements(user: User, stats: PlayerStats, p_data: dict, room: Room) -> list:
        unlocked = []
        user_ach_codes = {ua.achievement.code for ua in user.achievements.all()}

        criteria = [
            ('first_win', stats.wins >= 1, 'First Blood', 'Win your very first quiz battle!'),
            ('quiz_master', stats.wins >= 5, 'Quiz Master', 'Achieve 5 battle victories!'),
            ('hot_streak', p_data.get('max_streak', 0) >= 4, 'On Fire', 'Hit a 4+ answer streak in a single match!'),
            ('speed_demon', p_data.get('avg_response_time', 99) <= 3.0 and p_data.get('correct_count', 0) >= 3, 'Speed Demon', 'Average under 3 seconds with high accuracy!'),
            ('perfect_round', p_data.get('correct_count', 0) == len(room.questions) and len(room.questions) >= 5, 'Flawless Victory', 'Score 100% correct answers in a full match!'),
        ]

        for code, condition, title, desc in criteria:
            if condition and code not in user_ach_codes:
                ach = Achievement.query.filter_by(code=code).first()
                if ach:
                    ua = UserAchievement(user_id=user.id, achievement_id=ach.id)
                    db.session.add(ua)
                    unlocked.append({'code': code, 'title': title, 'description': desc, 'icon': ach.icon})

        return unlocked

    # Chat Event
    @socketio.on('send_chat')
    def handle_send_chat(data):
        sid = request.sid
        room = room_manager.get_room_by_sid(sid)
        if not room:
            return
        player = room.get_player(sid)
        if not player:
            return

        raw_msg = data.get('message', '').strip()
        if not raw_msg or len(raw_msg) > 120:
            return

        chat_payload = {
            'sender': player.username,
            'avatar': player.avatar,
            'message': raw_msg,
            'timestamp': time.strftime('%H:%M')
        }
        emit('chat_received', chat_payload, room=room.code)

    # Quick Match Queue Handlers
    @socketio.on('join_quick_match')
    def handle_join_quick_match():
        sid = request.sid
        user_id = session.get('user_id')
        username = session.get('username')
        avatar = session.get('avatar', 'cyber_ninja')
        is_guest = session.get('is_guest', False)

        if not user_id or not username:
            emit('error_message', {'message': 'Please sign in to join Quick Match.'})
            return

        # Add to quick queue
        room_manager.add_to_quick_queue({
            'sid': sid,
            'user_id': user_id,
            'username': username,
            'avatar': avatar,
            'is_guest': is_guest
        })

        emit('quick_match_queued', {'status': 'searching', 'message': 'Searching for an opponent...'})

        # Check if we have 2 players in queue to match!
        pair = room_manager.pop_quick_match_pair()
        if pair:
            p1_info, p2_info = pair
            p1_state = PlayerState(p1_info['sid'], p1_info['user_id'], p1_info['username'], p1_info['avatar'], p1_info['is_guest'])
            p2_state = PlayerState(p2_info['sid'], p2_info['user_id'], p2_info['username'], p2_info['avatar'], p2_info['is_guest'])
            
            p1_state.is_ready = True
            p2_state.is_ready = True

            new_room = room_manager.create_room(p1_info['sid'], p1_state, game_mode='pvp')
            room_manager.join_room(new_room.code, p2_state)

            socketio.emit('quick_match_found', {'room_code': new_room.code}, room=p1_info['sid'])
            socketio.emit('quick_match_found', {'room_code': new_room.code}, room=p2_info['sid'])

    @socketio.on('leave_quick_match')
    def handle_leave_quick_match():
        room_manager.remove_from_quick_queue(request.sid)
        emit('quick_match_cancelled', {'message': 'Left matchmaking queue.'})
