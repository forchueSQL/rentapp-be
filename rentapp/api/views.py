from rest_framework import generics
from .models import  User, Property, PropertyPhoto, Inquiry, PropertyStatus
from .serializers import UserSerializer, PropertySerializer, PropertyPhotoSerializer, InquirySerializer, PropertyStatusSerializer



class UserList(generics.ListCreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class PropertyList(generics.ListCreateAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Property.objects.all()
    serializer_class = PropertySerializer

class PropertyPhotoList(generics.ListCreateAPIView):
    queryset = PropertyPhoto.objects.all()
    serializer_class = PropertyPhotoSerializer

class PropertyPhotoDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyPhoto.objects.all()
    serializer_class = PropertyPhotoSerializer

class InquiryList(generics.ListCreateAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

class InquiryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Inquiry.objects.all()
    serializer_class = InquirySerializer

class PropertyStatusList(generics.ListCreateAPIView):
    queryset = PropertyStatus.objects.all()
    serializer_class = PropertyStatusSerializer

class PropertyStatusDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = PropertyStatus.objects.all()
    serializer_class = PropertyStatusSerializer

