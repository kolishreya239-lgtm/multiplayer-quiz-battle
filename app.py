import os
from flask import Flask
from flask_socketio import SocketIO
from config import Config
from models import db
from routes.auth import auth_bp
from routes.main import main_bp
from routes.dashboard import dashboard_bp
from routes.leaderboard import leaderboard_bp
from routes.profile import profile_bp
from routes.admin import admin_bp
from game.events import register_socket_events

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    
    # Initialize SocketIO with threading async mode for maximum Windows compatibility
    socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

    # Register blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(leaderboard_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(admin_bp)

    # Register SocketIO event handlers
    register_socket_events(socketio, app)

    # Inject global template helpers
    @app.context_processor
    def inject_globals():
        return {
            'app_name': 'QUIZ CLASH',
            'tagline': 'Think Fast. Answer Faster. Win the Battle.',
            'current_year': 2026
        }

    # Create tables and auto-seed if necessary
    with app.app_context():
        db.create_all()
        # Import and run seed
        try:
            from seed_data import seed_database
            seed_database(app)
        except Exception as e:
            print(f"[Seed Notice]: {e}")

    return app, socketio

app, socketio = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"\n==========================================================")
    print(f"  ⚡ QUIZ CLASH - MULTIPLAYER QUIZ BATTLE GAME ⚡")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"  Demo Accounts:")
    print(f"    - admin       / admin123  (Administrator)")
    print(f"    - cyber_ninja / demo123   (Player 1)")
    print(f"    - pixel_queen / demo123   (Player 2)")
    print(f"==========================================================\n")
    socketio.run(app, host='0.0.0.0', port=port, debug=True, allow_unsafe_werkzeug=True)
