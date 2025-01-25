from django.urls import path
from .views import (
    UserList, UserDetail,
    PropertyList, PropertyDetail,
    PropertyPhotoList, PropertyPhotoDetail,
    InquiryList, InquiryDetail,
    PropertyStatusList, PropertyStatusDetail
)

urlpatterns = [
    # User endpoints
    path('users/', UserList.as_view(), name='user-list'),
    path('users/<int:pk>/', UserDetail.as_view(), name='user-detail'),

    # Property endpoints
    path('properties/', PropertyList.as_view(), name='property-list'),
    path('properties/<int:pk>/', PropertyDetail.as_view(), name='property-detail'),

    # Property Photo endpoints
    path('property-photos/', PropertyPhotoList.as_view(), name='propertyphoto-list'),
    path('property-photos/<int:pk>/', PropertyPhotoDetail.as_view(), name='propertyphoto-detail'),

    # Inquiry endpoints
    path('inquiries/', InquiryList.as_view(), name='inquiry-list'),
    path('inquiries/<int:pk>/', InquiryDetail.as_view(), name='inquiry-detail'),

    # Property Status endpoints
    path('property-status/', PropertyStatusList.as_view(), name='propertystatus-list'),
    path('property-status/<int:pk>/', PropertyStatusDetail.as_view(), name='propertystatus-detail'),
]