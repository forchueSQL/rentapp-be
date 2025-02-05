from flask import Blueprint, request
from flask_restx import Resource, fields
from app import db, api
from app.models.models import Property, PropertyPhoto, PropertyStatus, Inquiry, Like, Comment
from app.schemas.schemas import (
    PropertySchema, PropertyPhotoSchema, PropertyStatusSchema,
    InquirySchema, LikeSchema, CommentSchema
)
from app.routes.auth import token_required, role_required

property_bp = Blueprint('property', __name__, url_prefix='/api')
property_ns = api.namespace(
    'property',
    description='Property management endpoints for RentApp'
)

# API Models for documentation
property_model = property_ns.model('Property', {
    'id': fields.Integer(readonly=True, description='Property ID', example=1),
    'title': fields.String(required=True, description='Property title', example='Beautiful 3-bedroom apartment'),
    'description': fields.String(description='Property description', example='Spacious apartment in the city center'),
    'price': fields.Float(required=True, description='Property price', example=1500.0),
    'address': fields.String(required=True, description='Property address', example='123 Main St'),
    'city': fields.String(required=True, description='City', example='New York'),
    'state': fields.String(required=True, description='State', example='NY'),
    'zip_code': fields.String(required=True, description='ZIP code', example='10001'),
    'property_type': fields.String(required=True, description='Type of property', enum=['apartment', 'house'], example='apartment'),
    'bedrooms': fields.Integer(required=True, description='Number of bedrooms', example=3),
    'bathrooms': fields.Integer(required=True, description='Number of bathrooms', example=2),
    'square_feet': fields.Integer(description='Square footage', example=1200),
    'broker_id': fields.Integer(required=True, description='Broker ID', example=1),
    'created_at': fields.DateTime(readonly=True, description='Creation date', example='2025-01-01T00:00:00Z')
})

property_status_model = property_ns.model('PropertyStatus', {
    'status': fields.String(required=True, description='Property status', enum=['available', 'rented', 'pending'])
})

property_photo_model = property_ns.model('PropertyPhoto', {
    'photo_url': fields.String(required=True, description='URL of the property photo')
})

inquiry_model = property_ns.model('Inquiry', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'message': fields.String(required=True, description='Inquiry message')
})

like_model = property_ns.model('Like', {
    'user_id': fields.Integer(required=True, description='User ID')
})

comment_model = property_ns.model('Comment', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'content': fields.String(required=True, description='Comment content')
})

@property_ns.route('/properties')
class Properties(Resource):
    @property_ns.doc('list_properties')
    @property_ns.response(200, 'Success')
    def get(self):
        """List all properties"""
        properties = Property.query.all()
        return PropertySchema(many=True).dump(properties)

    @property_ns.doc('create_property')
    @property_ns.expect(property_model)
    @property_ns.response(201, 'Property created')
    @token_required
    @role_required(['broker', 'admin'])
    def post(self, current_user):
        """Create a new property (Broker/Admin only)"""
        data = request.get_json()
        property = Property(
            title=data['title'],
            description=data.get('description'),
            price=data['price'],
            address=data['address'],
            city=data['city'],
            state=data['state'],
            zip_code=data['zip_code'],
            property_type=data['property_type'],
            bedrooms=data['bedrooms'],
            bathrooms=data['bathrooms'],
            square_feet=data.get('square_feet'),
            broker_id=current_user.id
        )
        db.session.add(property)
        db.session.commit()
        return PropertySchema().dump(property), 201

@property_ns.route('/properties/<int:property_id>')
class PropertyResource(Resource):
    @property_ns.doc('get_property')
    @property_ns.response(200, 'Success')
    @property_ns.response(404, 'Property not found')
    def get(self, property_id):
        """Get a specific property"""
        property = Property.query.get_or_404(property_id)
        return PropertySchema().dump(property)

    @property_ns.doc('update_property')
    @property_ns.expect(property_model)
    @property_ns.response(200, 'Property updated')
    @property_ns.response(404, 'Property not found')
    @token_required
    @role_required(['broker', 'admin'])
    def put(self, current_user, property_id):
        """Update a property (Broker/Admin only)"""
        property = Property.query.get_or_404(property_id)
        if property.broker_id != current_user.id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
            
        data = request.get_json()
        for key, value in data.items():
            setattr(property, key, value)
        
        db.session.commit()
        return PropertySchema().dump(property)

    @property_ns.doc('delete_property')
    @property_ns.response(204, 'Property deleted')
    @property_ns.response(404, 'Property not found')
    @token_required
    @role_required(['broker', 'admin'])
    def delete(self, current_user, property_id):
        """Delete a property (Broker/Admin only)"""
        property = Property.query.get_or_404(property_id)
        if property.broker_id != current_user.id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
            
        db.session.delete(property)
        db.session.commit()
        return '', 204

@property_ns.route('/properties/<int:property_id>/inquiries')
class PropertyInquiries(Resource):
    @property_ns.doc('get_property_inquiries')
    @property_ns.response(200, 'Success')
    def get(self, property_id):
        """Get all inquiries for a property"""
        inquiries = Inquiry.query.filter_by(property_id=property_id).all()
        return InquirySchema(many=True).dump(inquiries)

    @property_ns.doc('create_property_inquiry')
    @property_ns.expect(inquiry_model)
    @property_ns.response(201, 'Inquiry created')
    def post(self, property_id):
        """Create a new inquiry for a property (Customer only)"""
        data = request.get_json()
        inquiry = Inquiry(
            property_id=property_id,
            customer_id=data['customer_id'],
            message=data['message']
        )
        db.session.add(inquiry)
        db.session.commit()
        return InquirySchema().dump(inquiry), 201

@property_ns.route('/properties/<int:property_id>/likes')
class PropertyLikes(Resource):
    @property_ns.doc('get_property_likes')
    @property_ns.response(200, 'Success')
    def get(self, property_id):
        """Get all likes for a property"""
        likes = Like.query.filter_by(property_id=property_id).all()
        return LikeSchema(many=True).dump(likes)

    @property_ns.doc('create_property_like')
    @property_ns.expect(like_model)
    @property_ns.response(201, 'Like created')
    @property_ns.response(400, 'Already liked')
    def post(self, property_id):
        """Add a like to a property"""
        data = request.get_json()
        existing_like = Like.query.filter_by(
            property_id=property_id,
            user_id=data['user_id']
        ).first()
        
        if existing_like:
            property_ns.abort(400, "User has already liked this property")
            
        like = Like(
            property_id=property_id,
            user_id=data['user_id']
        )
        db.session.add(like)
        db.session.commit()
        return LikeSchema().dump(like), 201

@property_ns.route('/properties/<int:property_id>/status')
class PropertyStatus(Resource):
    @property_ns.doc('get_property_status')
    @property_ns.response(200, 'Success')
    def get(self, property_id):
        """Get property status"""
        status = PropertyStatus.query.filter_by(property_id=property_id).first()
        return PropertyStatusSchema().dump(status)

    @property_ns.doc('update_property_status')
    @property_ns.expect(property_status_model)
    @property_ns.response(200, 'Status updated')
    @token_required
    @role_required(['broker', 'admin'])
    def put(self, current_user, property_id):
        """Update property status (Broker/Admin only)"""
        property = Property.query.get_or_404(property_id)
        if property.broker_id != current_user.id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
            
        data = request.get_json()
        status = PropertyStatus.query.filter_by(property_id=property_id).first()
        if not status:
            status = PropertyStatus(property_id=property_id)
            db.session.add(status)
        
        status.status = data['status']
        db.session.commit()
        return PropertyStatusSchema().dump(status)

@property_ns.route('/properties/<int:property_id>/photos')
class PropertyPhotos(Resource):
    @property_ns.doc('get_property_photos')
    @property_ns.response(200, 'Success')
    def get(self, property_id):
        """Get all photos for a property"""
        photos = PropertyPhoto.query.filter_by(property_id=property_id).all()
        return PropertyPhotoSchema(many=True).dump(photos)

    @property_ns.doc('add_property_photo')
    @property_ns.expect(property_photo_model)
    @property_ns.response(201, 'Photo added')
    @token_required
    @role_required(['broker', 'admin'])
    def post(self, current_user, property_id):
        """Add a photo to a property (Broker/Admin only)"""
        property = Property.query.get_or_404(property_id)
        if property.broker_id != current_user.id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
            
        data = request.get_json()
        photo = PropertyPhoto(
            property_id=property_id,
            photo_url=data['photo_url']
        )
        db.session.add(photo)
        db.session.commit()
        return PropertyPhotoSchema().dump(photo), 201

@property_ns.route('/properties/<int:property_id>/photos/<int:photo_id>')
class PropertyPhotoResource(Resource):
    @property_ns.doc('delete_property_photo')
    @property_ns.response(204, 'Photo deleted')
    @property_ns.response(404, 'Photo not found')
    @token_required
    @role_required(['broker', 'admin'])
    def delete(self, current_user, property_id, photo_id):
        """Delete a property photo (Broker/Admin only)"""
        property = Property.query.get_or_404(property_id)
        if property.broker_id != current_user.id and current_user.role != 'admin':
            return {'message': 'Unauthorized'}, 403
            
        photo = PropertyPhoto.query.get_or_404(photo_id)
        if photo.property_id != property_id:
            return {'message': 'Photo not found'}, 404
            
        db.session.delete(photo)
        db.session.commit()
        return '', 204

@property_ns.route('/properties/<int:property_id>/comments')
class PropertyComments(Resource):
    @property_ns.doc('get_property_comments')
    @property_ns.response(200, 'Success')
    def get(self, property_id):
        """Get all comments for a property"""
        comments = Comment.query.filter_by(property_id=property_id).all()
        return CommentSchema(many=True).dump(comments)

    @property_ns.doc('create_property_comment')
    @property_ns.expect(comment_model)
    @property_ns.response(201, 'Comment created')
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
