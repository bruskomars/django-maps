from django.conf.urls import include
from . import views
from django.urls import path

urlpatterns = [
    path('city/', views.AdminCityListView.as_view(), name='admin-city-list'),
    path('landmark/', views.LandmarkListView.as_view(), name='landmark-list'),
    path('road/', views.RoadListView.as_view(), name='road-list'),
]