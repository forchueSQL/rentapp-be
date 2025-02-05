from flask import Blueprint, request
from flask_restx import Resource, fields
from app import db, api
from app.models.models import User
from app.schemas.schemas import UserSchema
from app.routes.auth import token_required, role_required

user_bp = Blueprint('user', __name__, url_prefix='/api')
user_ns = api.namespace(
    'user',
    description='User management endpoints for RentApp'
)

# API Models for documentation
user_model = user_ns.model('User', {
    'id': fields.Integer(description='User ID', readonly=True, example=1),
    'username': fields.String(required=True, description='Username (3-50 characters)', min_length=3, max_length=50, example='john_doe'),
    'email': fields.String(required=True, description='Email address', pattern=r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$', example='john@example.com'),
    'phone_number': fields.String(description='Phone number (digits only, max 15)', max_length=15, example='1234567890'),
    'role': fields.String(required=True, description='User role', enum=['admin', 'broker', 'customer'], example='customer'),
    'created_at': fields.DateTime(description='Account creation date', readonly=True, example='2025-01-01T00:00:00Z')
})

error_model = user_ns.model('Error', {
    'message': fields.String(description='Error message', example='An error occurred')
})

success_model = user_ns.model('Success', {
    'message': fields.String(description='Success message', example='Operation successful')
})

user_list_model = user_ns.model('UserList', {
    'users': fields.List(fields.Nested(user_model))
})

@user_ns.route('/users')
class Users(Resource):
    @user_ns.doc('list_users',
             description='List all users (Admin only)',
             security='Bearer Auth',
             responses={
                 200: ('Success', user_list_model),
                 403: ('Forbidden - Admin access required', error_model)
             })
    @token_required
    @role_required(['admin'])
    def get(self, current_user):
        users = User.query.all()
        return UserSchema(many=True, exclude=['password_hash']).dump(users)

    @user_ns.doc('create_user',
             description='Create a new user account (Admin only)',
             security='Bearer Auth',
             responses={
                 201: ('User created', user_model),
                 400: ('Validation error', error_model),
                 403: ('Forbidden - Admin access required', error_model),
                 409: ('Conflict - email/username already exists', error_model)
             })
    @user_ns.expect(user_model)
    @token_required
    @role_required(['admin'])
    def post(self, current_user):
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return UserSchema(exclude=['password_hash']).dump(user), 201

@user_ns.route('/users/<int:user_id>')
class UserResource(Resource):
    @user_ns.doc('get_user')
    @user_ns.response(200, 'Success')
    @user_ns.response(404, 'User not found')
    @token_required
    def get(self, current_user, user_id):
        """Get a specific user"""
        if current_user.id != user_id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
        user = User.query.get_or_404(user_id)
        return UserSchema(exclude=['password_hash']).dump(user)

    @user_ns.doc('update_user')
    @user_ns.expect(user_model)
    @user_ns.response(200, 'User updated')
    @user_ns.response(404, 'User not found')
    @token_required
    def put(self, current_user, user_id):
        """Update a user"""
        if current_user.id != user_id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        for key, value in data.items():
            if key != 'password_hash':  # Prevent direct password hash modification
                setattr(user, key, value)
            
        db.session.commit()
        return UserSchema(exclude=['password_hash']).dump(user)

    @user_ns.doc('delete_user')
    @user_ns.response(204, 'User deleted')
    @user_ns.response(404, 'User not found')
    @token_required
    @role_required(['admin'])
    def delete(self, current_user, user_id):
        """Delete a user (Admin only)"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
