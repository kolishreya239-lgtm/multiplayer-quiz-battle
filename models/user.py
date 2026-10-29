from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from models import db

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(40), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    avatar = db.Column(db.String(50), default='cyber_ninja')
    is_guest = db.Column(db.Boolean, default=False)
    is_admin = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    last_active = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationships
    stats = db.relationship('PlayerStats', backref='user', uselist=False, cascade='all, delete-orphan')
    achievements = db.relationship('UserAchievement', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    participations = db.relationship('MatchParticipant', backref='user', lazy='dynamic')

    def set_password(self, password: str):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password_hash, password)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'avatar': self.avatar,
            'is_guest': self.is_guest,
            'is_admin': self.is_admin,
            'stats': self.stats.to_dict() if self.stats else {}
        }


class PlayerStats(db.Model):
    __tablename__ = 'player_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False, unique=True)
    total_games = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    losses = db.Column(db.Integer, default=0)
    draws = db.Column(db.Integer, default=0)
    total_score = db.Column(db.Integer, default=0)
    highest_score = db.Column(db.Integer, default=0)
    current_streak = db.Column(db.Integer, default=0)
    max_streak = db.Column(db.Integer, default=0)
    total_correct = db.Column(db.Integer, default=0)
    total_answered = db.Column(db.Integer, default=0)

    @property
    def win_rate(self) -> float:
        if self.total_games == 0:
            return 0.0
        return round((self.wins / self.total_games) * 100, 1)

    @property
    def accuracy(self) -> float:
        if self.total_answered == 0:
            return 0.0
        return round((self.total_correct / self.total_answered) * 100, 1)

    def to_dict(self):
        return {
            'total_games': self.total_games,
            'wins': self.wins,
            'losses': self.losses,
            'draws': self.draws,
            'win_rate': self.win_rate,
            'total_score': self.total_score,
            'highest_score': self.highest_score,
            'current_streak': self.current_streak,
            'max_streak': self.max_streak,
            'accuracy': self.accuracy,
            'total_correct': self.total_correct,
            'total_answered': self.total_answered
        }


class Achievement(db.Model):
    __tablename__ = 'achievements'

    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(50), unique=True, nullable=False)
    title = db.Column(db.String(80), nullable=False)
    description = db.Column(db.String(255), nullable=False)
    icon = db.Column(db.String(50), default='award')
    xp_points = db.Column(db.Integer, default=100)

    def to_dict(self):
        return {
            'id': self.id,
            'code': self.code,
            'title': self.title,
            'description': self.description,
            'icon': self.icon,
            'xp_points': self.xp_points
        }


class UserAchievement(db.Model):
    __tablename__ = 'user_achievements'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=False)
    achievement_id = db.Column(db.Integer, db.ForeignKey('achievements.id', ondelete='CASCADE'), nullable=False)
    unlocked_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    achievement = db.relationship('Achievement')

    __table_args__ = (
        db.UniqueConstraint('user_id', 'achievement_id', name='uq_user_achievement'),
    )
