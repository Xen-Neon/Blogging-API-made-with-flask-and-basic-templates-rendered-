# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_login import LoginManager

db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()
login_manager = LoginManager()
login_manager.login_view = 'auth.login'

def create_app(config_object='app.config.Config'):
    app = Flask(__name__)
    app.config.from_object(config_object)

    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    login_manager.init_app(app)
    
    # Register Blueprints
    from app.auth.routes import auth_bp
    app.register_blueprint(auth_bp, url_prefix='/auth')
    
    from app.posts.routes import posts_bp
    app.register_blueprint(posts_bp, url_prefix='/posts')
    
    from app.comments.routes import comments_bp
    app.register_blueprint(comments_bp, url_prefix='/comments')
    
    from app.likes.routes import likes_bp
    app.register_blueprint(likes_bp, url_prefix='/likes')
    
    # Optional: Default route
    @app.route('/')
    def index():
        from flask import redirect, url_for
        return redirect(url_for('posts.list_posts'))
    
    # Import models here to avoid circular import issues
    with app.app_context():
        from app import models  # This registers models with SQLAlchemy / Flask-Migrate
    
    return app
