from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from app import db
from app.models.models import User
from app.schemas.schemas import UserSchema
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from flask import current_app
from functools import wraps

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization')
        if not token:
            return f(None, *args, **kwargs)  # Allow access without token
        try:
            token = token.split()[1]  # Remove 'Bearer ' prefix
            data = jwt.decode(token, current_app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = User.query.get(data['user_id'])
            return f(current_user, *args, **kwargs)
        except:
            return f(None, *args, **kwargs)  # Allow access if token is invalid
    return decorated

def role_required(roles):
    def decorator(f):
        @wraps(f)
        def decorated_function(current_user, *args, **kwargs):
            if not current_user or current_user.role not in roles:
                return {'message': 'Unauthorized access'}, 403
            return f(current_user, *args, **kwargs)
        return decorated_function
    return decorator

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp, 
    title='Authentication API',
    version='1.0',
    description='Authentication endpoints for RentApp'
)

# API Models for documentation
user_model = api.model('User', {
    'id': fields.Integer(description='User ID', readonly=True, example=1),
    'username': fields.String(required=True, description='Username (3-50 characters)', min_length=3, max_length=50, example='john_doe'),
    'email': fields.String(required=True, description='Email address', pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', example='john@example.com'),
    'phone_number': fields.String(description='Phone number (digits only, max 15)', max_length=15, example='1234567890'),
    'role': fields.String(required=True, description='User role', enum=['admin', 'broker', 'customer'], example='customer'),
    'created_at': fields.DateTime(description='Account creation date', readonly=True, example='2025-01-01T00:00:00Z')
})

register_model = api.model('Register', {
    'username': fields.String(required=True, description='Username (3-50 characters)', min_length=3, max_length=50),
    'email': fields.String(required=True, description='Valid email address', pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'),
    'password': fields.String(required=True, description='Password (minimum 6 characters)', min_length=6),
    'phone_number': fields.String(required=False, description='Phone number (digits only, max 15)', max_length=15),
    'role': fields.String(required=True, description='User role', enum=['admin', 'broker', 'customer'])
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Registered email address'),
    'password': fields.String(required=True, description='Account password')
})

token_response_model = api.model('TokenResponse', {
    'token': fields.String(description='JWT access token'),
    'user': fields.Nested(user_model)
})

error_model = api.model('Error', {
    'message': fields.String(description='Error message')
})

