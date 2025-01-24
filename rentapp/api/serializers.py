from rest_framework import serializers
from .models import Apartment, Tenant, Lease, User, Property, PropertyPhoto, Inquiry, PropertyStatus

class ApartmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Apartment
        fields = '__all__'
