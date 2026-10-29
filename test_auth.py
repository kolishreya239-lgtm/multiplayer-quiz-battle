import pytest
from app import create_app
from config import Config
from models import db
from models.user import User, PlayerStats

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'
    SECRET_KEY = 'test-secret-key'

@pytest.fixture
def app_instance():
    app, _ = create_app(TestConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

def test_password_hashing(app_instance):
    with app_instance.app_context():
        u = User(username='test_ninja')
        u.set_password('supersecret123')
        assert u.password_hash != 'supersecret123'
        assert u.check_password('supersecret123') is True
        assert u.check_password('wrongpass') is False

def test_stats_calculations(app_instance):
    with app_instance.app_context():
        u = User(username='stat_master')
        u.set_password('pass')
        db.session.add(u)
        db.session.flush()

        stats = PlayerStats(
            user_id=u.id,
            total_games=10,
            wins=7,
            losses=3,
            total_correct=35,
            total_answered=40
        )
        db.session.add(stats)
        db.session.commit()

        assert stats.win_rate == 70.0
        assert stats.accuracy == 87.5
