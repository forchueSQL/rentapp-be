from app import db
from datetime import datetime
from sqlalchemy import Enum
from sqlalchemy.orm import validates
from sqlalchemy.schema import UniqueConstraint


class User(db.Model):
    __tablename__ = 'users'

    ROLE_CHOICES = ('admin', 'broker', 'customer')

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    role = db.Column(Enum(*ROLE_CHOICES, name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    properties = db.relationship('Property', backref='broker', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    inquiries = db.relationship('Inquiry', backref='customer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'


class Property(db.Model):
    __tablename__ = 'properties'

    PROPERTY_TYPE_CHOICES = ('apartment', 'house')

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    state = db.Column(db.String(100), nullable=False)
    zip_code = db.Column(db.String(10), nullable=False)
    property_type = db.Column(Enum(*PROPERTY_TYPE_CHOICES, name='property_types'), nullable=False)
    bedrooms = db.Column(db.Integer, nullable=False)
    bathrooms = db.Column(db.Integer, nullable=False)
    square_feet = db.Column(db.Integer, nullable=True)
    broker_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    photos = db.relationship('PropertyPhoto', backref='property', lazy=True, cascade='all, delete-orphan')
    inquiries = db.relationship('Inquiry', backref='property', lazy=True, cascade='all, delete-orphan')
    statuses = db.relationship('PropertyStatus', backref='property', lazy=True, cascade='all, delete-orphan')
    likes = db.relationship('Like', backref='property', lazy=True, cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='property', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Property {self.title}>'


class PropertyPhoto(db.Model):
    __tablename__ = 'property_photos'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    photo_url = db.Column(db.Text, nullable=False)
    uploaded_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Photo for Property {self.property_id}>'


class Inquiry(db.Model):
    __tablename__ = 'inquiries'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    customer_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Inquiry {self.id} for Property {self.property_id}>'


class PropertyStatus(db.Model):
    __tablename__ = 'property_statuses'

    STATUS_CHOICES = ['available', 'rented', 'pending']

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    status = db.Column(Enum(*STATUS_CHOICES, name='status_types'), nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('status')
    def validate_status(self, key, value):
        if value not in self.STATUS_CHOICES:
            raise ValueError(f'Invalid status. Must be one of: {", ".join(self.STATUS_CHOICES)}')
        return value

    def __repr__(self):
        return f'<Status {self.status} for Property {self.property_id}>'


class Like(db.Model):
    __tablename__ = 'likes'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Ensure a user can only like a property once
    __table_args__ = (
        UniqueConstraint('property_id', 'user_id', name='unique_property_user_like'),
    )

    def __repr__(self):
        return f'<Like by User {self.user_id} on Property {self.property_id}>'


class Comment(db.Model):
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    @validates('content')
    def validate_content(self, key, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('Comment content cannot be empty')
        return value

    def __repr__(self):
        return f'<Comment {self.id} by User {self.user_id}>'