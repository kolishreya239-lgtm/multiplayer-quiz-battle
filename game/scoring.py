import math
from config import Config

def calculate_score(is_correct: bool, time_taken: float, question_time: int, current_streak: int) -> dict:
    """
    Server-side scoring engine:
    - Base score: 100 points for correct answer
    - Speed bonus: 0 to 50 points based on how quickly the answer was provided
    - Streak bonus: +20 points per consecutive correct answer (capped at 100)
    - Returns points earned, streak count, speed bonus, streak bonus
    """
    if not is_correct:
        return {
            'points': 0,
            'base': 0,
            'speed_bonus': 0,
            'streak_bonus': 0,
            'new_streak': 0,
            'is_correct': False
        }

    # Base points
    base = Config.BASE_POINTS_CORRECT

    # Speed bonus: faster answer yields more points
    safe_time = max(0.1, min(time_taken, float(question_time)))
    remaining_ratio = max(0.0, (question_time - safe_time) / question_time)
    speed_bonus = int(round(remaining_ratio * Config.MAX_SPEED_BONUS))

    # Streak bonus
    new_streak = current_streak + 1
    # Streak bonus activates starting from 2nd consecutive correct answer
    if new_streak > 1:
        streak_bonus = min((new_streak - 1) * Config.STREAK_BONUS_STEP, Config.MAX_STREAK_BONUS)
    else:
        streak_bonus = 0

    total_points = base + speed_bonus + streak_bonus

    return {
        'points': total_points,
        'base': base,
        'speed_bonus': speed_bonus,
        'streak_bonus': streak_bonus,
        'new_streak': new_streak,
        'is_correct': True
    }


def compute_final_ranks(players_scores: list) -> list:
    """
    Ranks players by score descending. Handles ties gracefully.
    players_scores: list of dicts [{'sid': ..., 'username': ..., 'score': ..., ...}]
    """
    sorted_players = sorted(players_scores, key=lambda p: (p.get('score', 0), -p.get('avg_response_time', 999)), reverse=True)
    
    current_rank = 1
    for i, player in enumerate(sorted_players):
        if i > 0:
            prev = sorted_players[i - 1]
            if prev.get('score', 0) == player.get('score', 0):
                player['rank'] = prev['rank']
            else:
                player['rank'] = i + 1
        else:
            player['rank'] = 1
            
    return sorted_players
