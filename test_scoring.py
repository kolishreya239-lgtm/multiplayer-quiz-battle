import pytest
from game.scoring import calculate_score, compute_final_ranks

def test_correct_answer_base_score():
    # If correct with time taken equal to total time -> gets 100 base, 0 speed bonus
    res = calculate_score(is_correct=True, time_taken=15.0, question_time=15, current_streak=0)
    assert res['is_correct'] is True
    assert res['base'] == 100
    assert res['speed_bonus'] == 0
    assert res['streak_bonus'] == 0
    assert res['points'] == 100
    assert res['new_streak'] == 1

def test_speed_bonus():
    # If answered quickly (e.g. 1 second out of 15 seconds)
    res = calculate_score(is_correct=True, time_taken=1.0, question_time=15, current_streak=0)
    assert res['speed_bonus'] > 40
    assert res['points'] > 140

def test_streak_bonus_escalation():
    # 1st correct: streak 1 -> 0 streak bonus
    s1 = calculate_score(is_correct=True, time_taken=10.0, question_time=15, current_streak=0)
    assert s1['new_streak'] == 1
    assert s1['streak_bonus'] == 0

    # 2nd correct: current_streak 1 -> new_streak 2 -> +20 streak bonus
    s2 = calculate_score(is_correct=True, time_taken=10.0, question_time=15, current_streak=1)
    assert s2['new_streak'] == 2
    assert s2['streak_bonus'] == 20

    # 3rd correct: current_streak 2 -> new_streak 3 -> +40 streak bonus
    s3 = calculate_score(is_correct=True, time_taken=10.0, question_time=15, current_streak=2)
    assert s3['new_streak'] == 3
    assert s3['streak_bonus'] == 40

def test_incorrect_answer():
    res = calculate_score(is_correct=False, time_taken=2.0, question_time=15, current_streak=5)
    assert res['is_correct'] is False
    assert res['points'] == 0
    assert res['new_streak'] == 0

def test_ranking_and_ties():
    players = [
        {'username': 'PlayerA', 'score': 300, 'avg_response_time': 3.5},
        {'username': 'PlayerB', 'score': 500, 'avg_response_time': 2.1},
        {'username': 'PlayerC', 'score': 300, 'avg_response_time': 1.8},
    ]
    ranked = compute_final_ranks(players)
    assert ranked[0]['username'] == 'PlayerB'
    assert ranked[0]['rank'] == 1
    # PlayerC had faster avg_response_time with same score, so should rank higher or tie
    assert ranked[1]['username'] == 'PlayerC'
