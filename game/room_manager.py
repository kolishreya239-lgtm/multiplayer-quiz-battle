import random
import string
import time
from typing import Dict, Optional, List
from config import Config

class PlayerState:
    def __init__(self, sid: str, user_id: int, username: str, avatar: str, is_guest: bool = False):
        self.sid = sid
        self.user_id = user_id
        self.username = username
        self.avatar = avatar
        self.is_guest = is_guest
        self.is_ready = False
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.correct_count = 0
        self.total_answered = 0
        self.total_time_taken = 0.0
        self.current_answer = None  # { 'option': 'A', 'time_taken': 1.4, 'points': 140, 'is_correct': True }
        self.connected = True

    def reset_for_game(self):
        self.score = 0
        self.streak = 0
        self.max_streak = 0
        self.correct_count = 0
        self.total_answered = 0
        self.total_time_taken = 0.0
        self.current_answer = None

    def to_dict(self):
        return {
            'sid': self.sid,
            'user_id': self.user_id,
            'username': self.username,
            'avatar': self.avatar,
            'is_guest': self.is_guest,
            'is_ready': self.is_ready,
            'score': self.score,
            'streak': self.streak,
            'max_streak': self.max_streak,
            'correct_count': self.correct_count,
            'total_answered': self.total_answered,
            'avg_response_time': round(self.total_time_taken / max(1, self.total_answered), 2),
            'has_answered': self.current_answer is not None,
            'connected': self.connected
        }


class Room:
    def __init__(self, code: str, host_sid: str, game_mode: str = 'pvp'):
        self.code = code
        self.host_sid = host_sid
        self.game_mode = game_mode  # 'pvp', 'quick_match', 'practice'
        self.state = 'waiting'      # 'waiting', 'in_progress', 'intermission', 'finished'
        self.players: Dict[str, PlayerState] = {}  # sid -> PlayerState
        
        # Match settings
        self.category_id: Optional[int] = None
        self.category_name: str = 'All Categories'
        self.difficulty: str = 'all'  # 'all', 'easy', 'medium', 'hard'
        self.question_count: int = Config.DEFAULT_QUESTION_COUNT
        self.question_time: int = Config.DEFAULT_QUESTION_TIME
        
        # Runtime game state
        self.questions: List[dict] = []
        self.current_question_index: int = -1
        self.question_start_time: float = 0.0
        self.timer_job = None
        self.created_at: float = time.time()

    def add_player(self, player: PlayerState):
        self.players[player.sid] = player
        # First player added is automatically ready if practice, else host
        if len(self.players) == 1 and self.game_mode == 'practice':
            player.is_ready = True

    def remove_player(self, sid: str) -> Optional[PlayerState]:
        player = self.players.pop(sid, None)
        # If host left and there are other players, promote the next player to host
        if sid == self.host_sid and self.players:
            self.host_sid = next(iter(self.players.keys()))
        return player

    def get_player(self, sid: str) -> Optional[PlayerState]:
        return self.players.get(sid)

    def get_player_by_user_id(self, user_id: int) -> Optional[PlayerState]:
        for player in self.players.values():
            if player.user_id == user_id:
                return player
        return None

    def all_players_ready(self) -> bool:
        if len(self.players) == 0:
            return False
        if self.game_mode == 'practice':
            return True
        return all(p.is_ready for p in self.players.values())

    def all_active_players_answered(self) -> bool:
        active = [p for p in self.players.values() if p.connected]
        if not active:
            return True
        return all(p.current_answer is not None for p in active)

    def get_current_question(self) -> Optional[dict]:
        if 0 <= self.current_question_index < len(self.questions):
            return self.questions[self.current_question_index]
        return None

    def reset_answers_for_round(self):
        for player in self.players.values():
            player.current_answer = None

    def to_dict(self):
        return {
            'code': self.code,
            'host_sid': self.host_sid,
            'game_mode': self.game_mode,
            'state': self.state,
            'player_count': len(self.players),
            'category_id': self.category_id,
            'category_name': self.category_name,
            'difficulty': self.difficulty,
            'question_count': self.question_count,
            'question_time': self.question_time,
            'current_question_index': self.current_question_index,
            'total_questions': len(self.questions),
            'players': [p.to_dict() for p in self.players.values()]
        }


class RoomManager:
    def __init__(self):
        self.rooms: Dict[str, Room] = {}
        self.quick_match_queue: List[dict] = []  # [{'sid': sid, 'user_id': uid, 'username': name, ...}]
        self.sid_to_room: Dict[str, str] = {}    # sid -> room_code

    def generate_room_code(self) -> str:
        while True:
            code = 'QC-' + ''.join(random.choices(string.digits, k=4))
            if code not in self.rooms:
                return code

    def create_room(self, host_sid: str, host_player: PlayerState, game_mode: str = 'pvp') -> Room:
        # Check if already in a room and leave it
        self.leave_room(host_sid)
        
        code = self.generate_room_code()
        room = Room(code=code, host_sid=host_sid, game_mode=game_mode)
        room.add_player(host_player)
        self.rooms[code] = room
        self.sid_to_room[host_sid] = code
        return room

    def get_room(self, code: str) -> Optional[Room]:
        if not code:
            return None
        return self.rooms.get(code.upper().strip())

    def get_room_by_sid(self, sid: str) -> Optional[Room]:
        code = self.sid_to_room.get(sid)
        if code:
            return self.rooms.get(code)
        return None

    def join_room(self, code: str, player: PlayerState) -> Optional[Room]:
        room = self.get_room(code)
        if not room:
            return None
        
        # Check if room is full or in progress
        if room.state != 'waiting':
            return None
            
        if len(room.players) >= 4:  # Room cap
            return None

        # Check if user already joined on a previous SID
        existing = room.get_player_by_user_id(player.user_id)
        if existing:
            # Reconnection or tab replacement
            self.sid_to_room.pop(existing.sid, None)
            room.players.pop(existing.sid, None)
            player.score = existing.score
            player.streak = existing.streak
            player.max_streak = existing.max_streak
            player.correct_count = existing.correct_count
            player.total_answered = existing.total_answered
            player.total_time_taken = existing.total_time_taken
            player.is_ready = existing.is_ready

        room.add_player(player)
        self.sid_to_room[player.sid] = room.code
        return room

    def leave_room(self, sid: str) -> Optional[Room]:
        code = self.sid_to_room.pop(sid, None)
        if not code:
            return None
        room = self.rooms.get(code)
        if room:
            room.remove_player(sid)
            if len(room.players) == 0:
                self.rooms.pop(code, None)
                return None
            return room
        return None

    def cleanup_old_rooms(self, max_age_seconds: int = 7200):
        """Cleanup rooms that have been inactive or abandoned for over 2 hours"""
        now = time.time()
        to_delete = [
            code for code, room in self.rooms.items()
            if now - room.created_at > max_age_seconds or len(room.players) == 0
        ]
        for code in to_delete:
            self.rooms.pop(code, None)

    def get_open_rooms(self) -> List[dict]:
        """Returns public rooms that are waiting for players"""
        return [
            room.to_dict() for room in self.rooms.values()
            if room.state == 'waiting' and room.game_mode == 'pvp' and len(room.players) < 4
        ]

    # Quick Match Matchmaking
    def add_to_quick_queue(self, player_info: dict):
        # Remove if already in queue
        self.quick_match_queue = [q for q in self.quick_match_queue if q['user_id'] != player_info['user_id']]
        self.quick_match_queue.append(player_info)

    def remove_from_quick_queue(self, sid: str):
        self.quick_match_queue = [q for q in self.quick_match_queue if q['sid'] != sid]

    def pop_quick_match_pair(self) -> Optional[tuple]:
        if len(self.quick_match_queue) >= 2:
            p1 = self.quick_match_queue.pop(0)
            p2 = self.quick_match_queue.pop(0)
            return p1, p2
        return None


# Global singleton instance
room_manager = RoomManager()
