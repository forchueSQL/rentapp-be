from flask import Blueprint, request
from flask_restx import Api, Resource, fields
from app import db
from app.models.models import Property, Inquiry, Like, Comment
from app.schemas.schemas import PropertySchema, InquirySchema, LikeSchema, CommentSchema
from app.routes.auth import token_required, role_required

property_bp = Blueprint('property', __name__)
api = Api(property_bp,
    title='Property API',
    version='1.0',
    description='Property management endpoints for RentApp'
)

# API Models for documentation
property_model = api.model('Property', {
    'title': fields.String(required=True, description='Property title'),
    'description': fields.String(description='Property description'),
    'price': fields.Float(required=True, description='Property price'),
    'address': fields.String(required=True, description='Property address'),
    'city': fields.String(required=True, description='City'),
    'state': fields.String(required=True, description='State'),
    'zip_code': fields.String(required=True, description='ZIP code'),
    'property_type': fields.String(required=True, description='Type of property', enum=['apartment', 'house']),
    'bedrooms': fields.Integer(required=True, description='Number of bedrooms'),
    'bathrooms': fields.Integer(required=True, description='Number of bathrooms'),
    'square_feet': fields.Integer(description='Square footage')
})

property_status_model = api.model('PropertyStatus', {
    'status': fields.String(required=True, description='Property status', enum=['available', 'rented', 'pending'])
})

property_photo_model = api.model('PropertyPhoto', {
    'photo_url': fields.String(required=True, description='URL of the property photo')
})

inquiry_model = api.model('Inquiry', {
    'customer_id': fields.Integer(required=True, description='Customer ID'),
    'message': fields.String(required=True, description='Inquiry message')
})

like_model = api.model('Like', {
    'user_id': fields.Integer(required=True, description='User ID')
})

comment_model = api.model('Comment', {
    'user_id': fields.Integer(required=True, description='User ID'),
    'content': fields.String(required=True, description='Comment content')
})

@api.route('/properties')
class Properties(Resource):
    @api.doc('list_properties')
    @api.response(200, 'Success')
    def get(self):
        """List all properties"""
        properties = Property.query.all()
        return PropertySchema(many=True).dump(properties)

    @api.doc('create_property')
    @api.expect(property_model)
    @api.response(201, 'Property created')
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

@api.route('/properties/<int:property_id>')
class PropertyResource(Resource):
    @api.doc('get_property')
    @api.response(200, 'Success')
    @api.response(404, 'Property not found')
    def get(self, property_id):
        """Get a specific property"""
        property = Property.query.get_or_404(property_id)
        return PropertySchema().dump(property)

    @api.doc('update_property')
    @api.expect(property_model)
    @api.response(200, 'Property updated')
    @api.response(404, 'Property not found')
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

    @api.doc('delete_property')
    @api.response(204, 'Property deleted')
    @api.response(404, 'Property not found')
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

    @api.doc('create_property')
    @api.expect(property_model)
    @api.response(201, 'Property created')
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

@api.route('/properties/<int:property_id>/inquiries')
class PropertyInquiries(Resource):
    @api.doc('get_property_inquiries')
    @api.response(200, 'Success')
    def get(self, property_id):
        """Get all inquiries for a property"""
        inquiries = Inquiry.query.filter_by(property_id=property_id).all()
        return InquirySchema(many=True).dump(inquiries)

    @api.doc('create_property_inquiry')
    @api.expect(inquiry_model)
    @api.response(201, 'Inquiry created')
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

@api.route('/properties/<int:property_id>/likes')
class PropertyLikes(Resource):
    @api.doc('get_property_likes')
    @api.response(200, 'Success')
    def get(self, property_id):
        """Get all likes for a property"""
        likes = Like.query.filter_by(property_id=property_id).all()
        return LikeSchema(many=True).dump(likes)

    @api.doc('create_property_like')
    @api.expect(like_model)
    @api.response(201, 'Like created')
    @api.response(400, 'Already liked')
    def post(self, property_id):
        """Add a like to a property"""
        data = request.get_json()
        existing_like = Like.query.filter_by(
            property_id=property_id,
            user_id=data['user_id']
        ).first()
        
        if existing_like:
            api.abort(400, "User has already liked this property")
            
        like = Like(
            property_id=property_id,
            user_id=data['user_id']
        )
        db.session.add(like)
        db.session.commit()
        return LikeSchema().dump(like), 201

@api.route('/properties/<int:property_id>/status')
class PropertyStatus(Resource):
    @api.doc('get_property_status')
    @api.response(200, 'Success')
    def get(self, property_id):
        """Get property status"""
        status = PropertyStatus.query.filter_by(property_id=property_id).first()
        return PropertyStatusSchema().dump(status)

    @api.doc('update_property_status')
    @api.expect(property_status_model)
    @api.response(200, 'Status updated')
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

@api.route('/properties/<int:property_id>/photos')
class PropertyPhotos(Resource):
    @api.doc('get_property_photos')
    @api.response(200, 'Success')
    def get(self, property_id):
        """Get all photos for a property"""
        photos = PropertyPhoto.query.filter_by(property_id=property_id).all()
        return PropertyPhotoSchema(many=True).dump(photos)

    @api.doc('add_property_photo')
    @api.expect(property_photo_model)
    @api.response(201, 'Photo added')
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

@api.route('/properties/<int:property_id>/photos/<int:photo_id>')
class PropertyPhotoResource(Resource):
    @api.doc('delete_property_photo')
    @api.response(204, 'Photo deleted')
    @api.response(404, 'Photo not found')
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

@api.route('/properties/<int:property_id>/comments')
class PropertyComments(Resource):
    @api.doc('get_property_comments')
    @api.response(200, 'Success')
    def get(self, property_id):
        """Get all comments for a property"""
        comments = Comment.query.filter_by(property_id=property_id).all()
        return CommentSchema(many=True).dump(comments)

    @api.doc('create_property_comment')
    @api.expect(comment_model)
    @api.response(201, 'Comment created')
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
