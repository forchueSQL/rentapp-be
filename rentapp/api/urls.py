from django.urls import path
from . import views

urlpatterns = [
    path('apartments/', views.ApartmentList.as_view(), name='apartment-list'),
    path('apartments/<int:pk>/', views.ApartmentDetail.as_view(), name='apartment-detail'),
]
