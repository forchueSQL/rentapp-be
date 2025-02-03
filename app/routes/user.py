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
    def get(self):
        """Get all users"""
        users = User.query.all()
        return UserSchema(many=True).dump(users)

@api.route('/users/<int:user_id>')
class UserResource(Resource):
    def get(self, user_id):
        """Get a specific user"""
        user = User.query.get_or_404(user_id)
        return UserSchema().dump(user)

    def put(self, user_id):
        """Update a user"""
        user = User.query.get_or_404(user_id)
        data = request.get_json()
        
        for key, value in data.items():
            setattr(user, key, value)
            
        db.session.commit()
        return UserSchema().dump(user)

    def delete(self, user_id):
        """Delete a user"""
        user = User.query.get_or_404(user_id)
        db.session.delete(user)
        db.session.commit()
        return '', 204
