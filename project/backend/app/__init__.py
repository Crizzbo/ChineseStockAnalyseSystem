from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_socketio import SocketIO
import os
from datetime import timedelta

# Initialize extensions
db = SQLAlchemy()
jwt = JWTManager()
migrate = Migrate()
socketio = SocketIO()
redis_client = None  # 禁用Redis

def create_app(config_name='development'):
    app = Flask(__name__)

    # Configuration
    app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    app.config['JWT_SECRET_KEY'] = os.getenv('JWT_SECRET_KEY', 'jwt-secret-key-change-in-production')
    app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(hours=24)
    app.config['JWT_REFRESH_TOKEN_EXPIRES'] = timedelta(days=30)

    # Database Configuration
    database_url = os.getenv('DATABASE_URL', 'sqlite:///stock_analysis.db')
    if database_url.startswith('postgres://'):
        database_url = database_url.replace('postgres://', 'postgresql://', 1)
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # Copilot AI Configuration
    from app.config.copilot_config import COPILOT_AI_CONFIG
    app.config['COPILOT_AI'] = COPILOT_AI_CONFIG

    # CORS Configuration - 允许所有来源用于开发
    CORS(app, origins="*", allow_headers="*", methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"])

    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    migrate.init_app(app, db)
    socketio.init_app(app, cors_allowed_origins="*", async_mode='threading')

    # Initialize AI Service
    from app.services.copilot_chat import copilot_chat_service

    # Register Blueprints
    from app.api.auth import auth_bp
    from app.api.stocks import stocks_bp
    from app.api.analysis import analysis_bp
    from app.api.portfolio import portfolio_bp
    from app.api.market import market_bp
    from app.api.sectors import sectors_bp
    from app.api.copilot_chat import ai_bp  # 使用新的Copilot AI服务
    from app.api.user import user_bp
    from app.api.test import test_bp
    from app.api.fundamental import fundamental_bp

    app.register_blueprint(auth_bp, url_prefix='/api/v1/auth')
    app.register_blueprint(stocks_bp, url_prefix='/api/v1/stocks')
    app.register_blueprint(analysis_bp, url_prefix='/api/v1/analysis')
    app.register_blueprint(portfolio_bp, url_prefix='/api/v1/portfolio')
    app.register_blueprint(market_bp, url_prefix='/api/v1/market')
    app.register_blueprint(sectors_bp, url_prefix='/api/v1/sectors')
    app.register_blueprint(ai_bp, url_prefix='/api/v1/ai')
    app.register_blueprint(user_bp, url_prefix='/api/v1/user')
    app.register_blueprint(test_bp, url_prefix='/api/v1/test')
    app.register_blueprint(fundamental_bp, url_prefix='/api/v1/fundamental')

    # Register WebSocket events
    from app.websocket import events

    # 添加CORS响应头
    @app.after_request
    def after_request(response):
        response.headers['Access-Control-Allow-Origin'] = '*'
        response.headers['Access-Control-Allow-Headers'] = 'Content-Type,Authorization,X-Requested-With'
        response.headers['Access-Control-Allow-Methods'] = 'GET,PUT,POST,DELETE,OPTIONS'
        response.headers['Access-Control-Allow-Credentials'] = 'true'
        return response

    # Error handlers
    from app.utils.error_handlers import register_error_handlers
    register_error_handlers(app)

    # Create database tables
    with app.app_context():
        try:
            db.create_all()
            app.logger.info("Database tables created successfully")
        except Exception as e:
            app.logger.error(f"Database initialization failed: {e}")

    return app