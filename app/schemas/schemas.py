from marshmallow import Schema, fields, validate, validates, ValidationError
from app.models.models import User, Property, PropertyPhoto, PropertyStatus, Inquiry, Like, Comment
from datetime import datetime

class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True, validate=validate.Length(min=3, max=50))
    password = fields.Str(required=True, load_only=True, validate=validate.Length(min=6))
    email = fields.Email(required=True)
    phone_number = fields.Str(validate=validate.Length(max=15))
    role = fields.Str(required=True, validate=validate.OneOf(User.ROLE_CHOICES))
    created_at = fields.DateTime(dump_only=True)

    @validates('phone_number')
    def validate_phone_number(self, value):
        if value and not value.isdigit():
            raise ValidationError('Phone number must contain only digits')

class PropertySchema(Schema):
    id = fields.Int(dump_only=True)
    title = fields.Str(required=True, validate=validate.Length(max=100))
    description = fields.Str()
    price = fields.Decimal(required=True, places=2)
    address = fields.Str(required=True, validate=validate.Length(max=255))
    city = fields.Str(required=True, validate=validate.Length(max=100))
    state = fields.Str(required=True, validate=validate.Length(max=100))
    zip_code = fields.Str(required=True, validate=validate.Length(max=10))
    property_type = fields.Str(required=True, validate=validate.OneOf(Property.PROPERTY_TYPE_CHOICES))
    bedrooms = fields.Int(required=True)
    bathrooms = fields.Int(required=True)
    square_feet = fields.Int()
    broker_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class PropertyPhotoSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    photo_url = fields.Url(required=True)
    uploaded_at = fields.DateTime(dump_only=True)

class PropertyStatusSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    status = fields.Str(required=True, validate=validate.OneOf(PropertyStatus.STATUS_CHOICES))
    updated_at = fields.DateTime(dump_only=True)

class InquirySchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    customer_id = fields.Int(required=True)
    message = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    created_at = fields.DateTime(dump_only=True)

class LikeSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    created_at = fields.DateTime(dump_only=True)

class CommentSchema(Schema):
    id = fields.Int(dump_only=True)
    property_id = fields.Int(required=True)
    user_id = fields.Int(required=True)
    content = fields.Str(required=True, validate=validate.Length(min=1, max=1000))
    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)
