from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from flask_migrate import Migrate
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

# Load configuration from .env
app.config.from_prefixed_env()

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'postgresql://user:password@localhost/rentapp')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
ma = Marshmallow(app)
migrate = Migrate(app, db)

# Import models and routes after db initialization to avoid circular imports
from .models import *
from .routes import *

if __name__ == '__main__':
    app.run(debug=True)
