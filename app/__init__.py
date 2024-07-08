# app/__init__.py
from flask import Flask
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from app.models import db
from app.config import Config

# Initialize extensions
migrate = Migrate()
jwt = JWTManager()

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions with app
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    # Create the database tables (if they don't exist)
    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.routes import main as main_blueprint
    app.register_blueprint(main_blueprint)

    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)


    return app
