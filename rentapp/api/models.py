from django.db import models
from django.core.validators import MinLengthValidator

class User(models.Model):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('broker', 'Broker'),
        ('customer', 'Customer'),
    ]

    username = models.CharField(max_length=50, unique=True)
    password_hash = models.TextField()
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username

class Property(models.Model):
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
    ]

    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    zip_code = models.CharField(max_length=10)
    property_type = models.CharField(max_length=50, choices=PROPERTY_TYPE_CHOICES)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    square_feet = models.IntegerField(blank=True, null=True)
    broker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

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
