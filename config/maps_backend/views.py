from rest_framework import generics
from .models import Admin, Landmark, Road
from .serializers import AdminSerializer, LandmarkSerializer, RoadSerializer
from django.http import Http404
from rest_framework.exceptions import ParseError

# Create your views here.
class AdminCityListView(generics.ListAPIView):
    
    serializer_class = AdminSerializer
    name = 'admin-city-list'
    
    def get_queryset(self):
        city = self.request.query_params.get('city', None)
        if city is None:
            raise ParseError("City parameter is required.")
        
        queryset = Admin.objects.filter(city__contains=city)
        
        if not queryset.exists():
            raise Http404(f"No Admin records found for city: {city}")
        
        return queryset

class LandmarkListView(generics.ListAPIView):
    serializer_class = LandmarkSerializer
    name = 'landmark-list'
    
    def get_queryset(self):
        landmark = self.request.query_params.get('name', None)
        
        if landmark is None:
            raise ParseError("Landmark parameter is required")
        
        queryset = Landmark.objects.filter(name__contains=landmark)
        
        if not queryset.exists():
            raise Http404(f"No Landmark records found for name: {landmark}")
        
        return queryset

class RoadListView(generics.ListAPIView):
    serializer_class = RoadSerializer
    name = 'road-list'
    
    def get_queryset(self):
        road = self.request.query_params.get('name', None)
        
        if road is None:
            raise ParseError("Road parameter is required")
        
        queryset = Road.objects.filter(name__contains=road)
        
        if not queryset.exists():
            raise Http404(f"No Road records found for name: {road}")
        
        return queryset
        
        
