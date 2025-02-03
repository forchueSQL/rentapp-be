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
register_model = api.model('Register', {
    'username': fields.String(required=True, description='Username'),
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password'),
    'phone_number': fields.String(required=False, description='Phone number'),
    'role': fields.String(required=True, description='User role (admin, broker, customer)')
})

login_model = api.model('Login', {
    'email': fields.String(required=True, description='Email address'),
    'password': fields.String(required=True, description='Password')
})

@api.route('/register')
class Register(Resource):
    @api.doc('register_user')
    @api.expect(register_model)
    @api.response(201, 'User successfully created')
    @api.response(400, 'Validation error')
    def post(self):
        """Register a new user"""
        data = request.get_json()
        
        if User.query.filter_by(email=data['email']).first():
            api.abort(400, "Email already registered")
            
        if User.query.filter_by(username=data['username']).first():
            api.abort(400, "Username already taken")
        
        user = User(
            username=data['username'],
            email=data['email'],
            password_hash=generate_password_hash(data['password']),
            role=data.get('role', 'customer'),
            phone_number=data.get('phone_number')
        )
        
        db.session.add(user)
        db.session.commit()
        
        return UserSchema(exclude=['password_hash']).dump(user), 201

@api.route('/login')
class Login(Resource):
    @api.doc('login_user')
    @api.expect(login_model)
    @api.response(200, 'Login successful')
    @api.response(401, 'Invalid credentials')
    def post(self):
        """Login and receive authentication token"""
        data = request.get_json()
        
        user = User.query.filter_by(email=data['email']).first()
        if not user or not check_password_hash(user.password_hash, data['password']):
            api.abort(401, "Invalid email or password")
        
        token = jwt.encode({
            'user_id': user.id,
            'exp': datetime.utcnow() + timedelta(days=1)
        }, current_app.config['SECRET_KEY'])
        
        return {
            'token': token,
            'user': UserSchema(exclude=['password_hash']).dump(user)
        }
