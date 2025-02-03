from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from app import db
from app.models.models import User
from app.schemas.schemas import UserSchema
from app.routes.auth import token_required, role_required

user_bp = Blueprint('user', __name__)
api = Api(user_bp,
    title='User API',
    version='1.0',
    description='User management endpoints for RentApp'
)

# API Models for documentation
user_model = api.model('User', {
    'username': fields.String(description='Username'),
    'email': fields.String(description='Email address'),
    'phone_number': fields.String(description='Phone number'),
    'role': fields.String(description='User role')
})

@api.route('/users')
class Users(Resource):
    @api.doc('list_users')
    @api.response(200, 'Success')
    @token_required
    @role_required(['admin'])
    def get(self, current_user):
        """Get all users (Admin only)"""
        users = User.query.all()
        return UserSchema(many=True, exclude=['password_hash']).dump(users)

    @api.doc('create_user')
    @api.expect(user_model)
    @api.response(201, 'User created')
    @token_required
    @role_required(['admin'])
    def post(self, current_user):
        """Create a new user (Admin only)"""
        data = request.get_json()
        if User.query.filter_by(email=data['email']).first():
            return {'message': 'Email already registered'}, 400
        
        user = User(**data)
        db.session.add(user)
        db.session.commit()
        return UserSchema(exclude=['password_hash']).dump(user), 201

@api.route('/users/<int:user_id>')
class UserResource(Resource):
    @api.doc('get_user')
    @api.response(200, 'Success')
    @api.response(404, 'User not found')
    @token_required
    def get(self, current_user, user_id):
        """Get a specific user"""
        if current_user.id != user_id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
        user = User.query.get_or_404(user_id)
        return UserSchema(exclude=['password_hash']).dump(user)

    @api.doc('update_user')
    @api.expect(user_model)
    @api.response(200, 'User updated')
    @api.response(404, 'User not found')
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

    @api.doc('delete_user')
    @api.response(204, 'User deleted')
    @api.response(404, 'User not found')
    @token_required
    @role_required(['admin'])
    def delete(self, current_user, user_id):
        """Delete a user (Admin only)"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
