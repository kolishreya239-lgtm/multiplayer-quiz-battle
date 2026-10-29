import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
INSTANCE_DIR = os.path.join(BASE_DIR, 'instance')
os.makedirs(INSTANCE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY', 'quiz-clash-cyber-secret-key-2026-x99')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', f"sqlite:///{os.path.join(INSTANCE_DIR, 'quiz_clash.db')}"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
    
    # Game Configuration
    BASE_POINTS_CORRECT = 100
    MAX_SPEED_BONUS = 50
    STREAK_BONUS_STEP = 20
    MAX_STREAK_BONUS = 100
    DEFAULT_QUESTION_TIME = 15  # seconds
    DEFAULT_QUESTION_COUNT = 5
    INTERMISSION_TIME = 4       # seconds between questions
    
    # Avatars available for players
    AVATARS = [
        'cyber_ninja', 'pixel_queen', 'neon_falcon', 'shadow_knight',
        'code_wizard', 'mecha_titan', 'quantum_ghost', 'turbo_fox'
    ]
