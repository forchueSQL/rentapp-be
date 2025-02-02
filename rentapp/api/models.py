from app import db
from datetime import datetime
from sqlalchemy import Enum

class User(db.Model):
    ROLE_CHOICES = ('admin', 'broker', 'customer')
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone_number = db.Column(db.String(15), nullable=True)
    role = db.Column(Enum(*ROLE_CHOICES, name='user_roles'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    properties = db.relationship('Property', backref='broker', lazy=True)
    likes = db.relationship('Like', backref='user', lazy=True)
    comments = db.relationship('Comment', backref='user', lazy=True)
    inquiries = db.relationship('Inquiry', backref='customer', lazy=True)

    def __repr__(self):
        return f'<User {self.username}>'

class Property(db.Model):
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
    broker_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    photos = db.relationship('PropertyPhoto', backref='property', lazy=True)
    inquiries = db.relationship('Inquiry', backref='property', lazy=True)
    statuses = db.relationship('PropertyStatus', backref='property', lazy=True)
    likes = db.relationship('Like', backref='property', lazy=True)
    comments = db.relationship('Comment', backref='property', lazy=True)

    def __repr__(self):
        return f'<Property {self.title}>'

class PropertyPhoto(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='photos')
    photo_url = models.TextField()
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Photo for {self.property.title}"

class Inquiry(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inquiries')
    customer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inquiries')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Inquiry by {self.customer.username} for {self.property.title}"

class PropertyStatus(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('rented', 'Rented'),
        ('pending', 'Pending'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='status')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.property.title}: {self.status}"

class Like(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('property', 'user')

    def __str__(self):
        return f"{self.user.username} likes {self.property.title}"

class Comment(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField(validators=[MinLengthValidator(1)])
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.property.title}"
