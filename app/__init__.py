from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_restx import Api
from config import Config

db = SQLAlchemy()
migrate = Migrate()

# Initialize the main API
api = Api(
    title='RentApp API',
    version='1.0',
    description='A complete API for property rental management',
    doc='/docs'  # Swagger UI will be available at /docs
)

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    db.init_app(app)
    migrate.init_app(app, db)

    # Initialize the main API with the app
    api.init_app(app)

    # Import blueprints
    from app.routes.auth import auth_bp
    from app.routes.property import property_bp
    from app.routes.user import user_bp

    # Register blueprints
    app.register_blueprint(auth_bp)
    app.register_blueprint(property_bp)
    app.register_blueprint(user_bp)

    return app
