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
        
        
