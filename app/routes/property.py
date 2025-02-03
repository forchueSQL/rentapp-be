from flask import Blueprint, request
from flask_restx import Api, Resource
from app import db
from app.models.models import Inquiry, Like, Comment
from app.schemas.schemas import InquirySchema, LikeSchema, CommentSchema

property_bp = Blueprint('property', __name__)
api = Api(property_bp)

@api.route('/properties/<int:property_id>/inquiries')
class PropertyInquiries(Resource):
    def get(self, property_id):
        """Get all inquiries for a property"""
        inquiries = Inquiry.query.filter_by(property_id=property_id).all()
        return InquirySchema(many=True).dump(inquiries)

    def post(self, property_id):
        """Create a new inquiry for a property"""
        data = request.get_json()
        inquiry = Inquiry(
            property_id=property_id,
            customer_id=data['customer_id'],
            message=data['message']
        )
        db.session.add(inquiry)
        db.session.commit()
        return InquirySchema().dump(inquiry), 201

@api.route('/properties/<int:property_id>/likes')
class PropertyLikes(Resource):
    def get(self, property_id):
        """Get all likes for a property"""
        likes = Like.query.filter_by(property_id=property_id).all()
        return LikeSchema(many=True).dump(likes)

    def post(self, property_id):
        """Add a like to a property"""
        data = request.get_json()
        like = Like(
            property_id=property_id,
            user_id=data['user_id']
        )
        db.session.add(like)
        db.session.commit()
        return LikeSchema().dump(like), 201

@api.route('/properties/<int:property_id>/comments')
class PropertyComments(Resource):
    def get(self, property_id):
        """Get all comments for a property"""
        comments = Comment.query.filter_by(property_id=property_id).all()
        return CommentSchema(many=True).dump(comments)

    def post(self, property_id):
        """Add a comment to a property"""
        data = request.get_json()
        comment = Comment(
            property_id=property_id,
            user_id=data['user_id'],
            content=data['content']
        )
        db.session.add(comment)
        db.session.commit()
        return CommentSchema().dump(comment), 201
