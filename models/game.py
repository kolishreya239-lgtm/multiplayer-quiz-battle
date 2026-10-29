from datetime import datetime, timezone
from models import db

class MatchHistory(db.Model):
    __tablename__ = 'match_history'

    id = db.Column(db.Integer, primary_key=True)
    room_code = db.Column(db.String(20), nullable=False)
    game_mode = db.Column(db.String(30), default='pvp')  # 'pvp', 'practice', 'quick_match', 'daily'
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=True)
    difficulty = db.Column(db.String(20), default='medium')
    total_questions = db.Column(db.Integer, default=5)
    winner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    is_draw = db.Column(db.Boolean, default=False)
    played_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    category = db.relationship('Category')
    winner = db.relationship('User', foreign_keys=[winner_id])
    participants = db.relationship('MatchParticipant', backref='match', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'room_code': self.room_code,
            'game_mode': self.game_mode,
            'category_name': self.category.name if self.category else 'Mixed',
            'difficulty': self.difficulty,
            'total_questions': self.total_questions,
            'winner_name': self.winner.username if self.winner else ('Draw' if self.is_draw else 'None'),
            'is_draw': self.is_draw,
            'played_at': self.played_at.strftime('%Y-%m-%d %H:%M'),
            'participants': [p.to_dict() for p in self.participants]
        }


class MatchParticipant(db.Model):
    __tablename__ = 'match_participants'

    id = db.Column(db.Integer, primary_key=True)
    match_id = db.Column(db.Integer, db.ForeignKey('match_history.id', ondelete='CASCADE'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    final_score = db.Column(db.Integer, default=0)
    rank = db.Column(db.Integer, default=1)
    correct_count = db.Column(db.Integer, default=0)
    total_answered = db.Column(db.Integer, default=0)
    avg_response_time = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'username': self.user.username if self.user else 'Guest',
            'avatar': self.user.avatar if self.user else 'cyber_ninja',
            'final_score': self.final_score,
            'rank': self.rank,
            'correct_count': self.correct_count,
            'total_answered': self.total_answered,
            'avg_response_time': round(self.avg_response_time, 2)
        }


class DailyChallengeRecord(db.Model):
    __tablename__ = 'daily_challenge_records'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    challenge_date = db.Column(db.String(10), nullable=False)  # 'YYYY-MM-DD'
    score = db.Column(db.Integer, default=0)
    correct_count = db.Column(db.Integer, default=0)
    total_questions = db.Column(db.Integer, default=5)
    completed_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', backref=db.backref('daily_records', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'challenge_date', name='uq_user_daily_date'),
    )

    def to_dict(self):
        return {
            'challenge_date': self.challenge_date,
            'score': self.score,
            'correct_count': self.correct_count,
            'total_questions': self.total_questions,
            'completed_at': self.completed_at.strftime('%Y-%m-%d %H:%M')
        }
