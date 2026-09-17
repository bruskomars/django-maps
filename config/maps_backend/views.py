from rest_framework import generics
from .models import Admin, Landmark, Road, Address
from .serializers import AdminSerializer, LandmarkSerializer, RoadSerializer, AddressSerializer, LandmarkGeoSerializer
from django.http import Http404
from rest_framework.exceptions import ParseError
import time

# Landmark Cross Model Search
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.gis.measure import D
from django.contrib.gis.db.models.aggregates import Union
from django.db import connection

# search address import
from django.contrib.postgres.search import TrigramSimilarity, TrigramWordSimilarity
from django.db.models.functions import Concat, Coalesce, Replace
from django.db.models import Value, CharField, F
import re
from rest_framework_gis.serializers import GeoFeatureModelSerializer

# utils
from .utils import *

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
        
        
class AddressListView(generics.ListAPIView):
    serializer_class = AddressSerializer
    name = 'address-list'
    
    def get_queryset(self):
        params = self.request.query_params
        hn = params.get('hn')
        street = params.get('street')
        subdivision = params.get('subd')
        barangay = params.get('brgy')
        municipality = params.get('city')

        if not any([hn, street, subdivision, barangay, municipality]):
            raise ParseError("At least one search field is required.")

        qs = Address.objects.all()
        THRESHOLD = 0.85  # tune this per field if needed

        # House number: exact match only, no fuzziness
        def normalize_hn(value):
            return value.replace(' ', '').replace('-', '')
        
        STREET_SUFFIXES = r'\b(street|st\.?|avenue|ave\.?|avenida|road|rd\.?|boulevard|blvd\.?|drive|dr\.?|lane|ln\.?|calle)\b'
        
        def strip_suffix(value):
            cleaned = re.sub(STREET_SUFFIXES, '', value, flags=re.IGNORECASE)
            cleaned = re.sub(r'\s+', ' ', cleaned).strip()
            return cleaned
        
        if hn:
            hn_normalized = normalize_hn(hn)
            escaped = re.escape(hn_normalized)
            pattern = rf'^{escaped}$|^{escaped}[^0-9]'

            qs = qs.annotate(
                hn_normalized=Replace(
                    Replace('hn', Value(' '), Value(''), output_field=CharField()),
                    Value('-'), Value(''), output_field=CharField()
                )
            ).filter(hn_normalized__iregex=pattern)

        similarity_fields = []

        if street:
            street_clean = strip_suffix(street) or street
            qs = qs.annotate(street_sim=TrigramWordSimilarity(street_clean, 'street_base_name'))
            qs = qs.filter(street_sim__gt=.5)
            similarity_fields.append('street_sim')
            
        if barangay:
            qs = qs.annotate(brgy_sim=TrigramSimilarity('barangay', barangay))
            qs = qs.filter(brgy_sim__gt=.4)
            similarity_fields.append('brgy_sim')

        if municipality:
            qs = qs.annotate(city_sim=TrigramSimilarity('municipality', municipality))
            qs = qs.filter(city_sim__gt=.4)
            similarity_fields.append('city_sim')

        if subdivision:
            qs = qs.annotate(subd_sim=TrigramSimilarity('subdivision', subdivision))
            qs = qs.filter(subd_sim__gt=.5)
            similarity_fields.append('subd_sim')

        # Rank by combined similarity across whichever fields were actually searched
        if similarity_fields:
            combined_expr = F(similarity_fields[0])
            for field in similarity_fields[1:]:
                combined_expr = combined_expr + F(field)
            qs = qs.annotate(combined_score=combined_expr).order_by('-combined_score')

        if not qs.exists():
            raise Http404("No matching address points found.")

        return qs[:5]
    
class CrossModelSearchView(APIView):
    def get(self, request):
        params = self.request.query_params
        landmark = params.get('landmark')
        hn = params.get('hn')
        street = params.get('street')
        subdivision = params.get('subd')
        barangay = params.get('brgy')
        municipality = params.get('city')
        
        results = {}
        
        if landmark:
            landmarks = self.search_landmark(
                landmark, barangay=barangay, city=municipality, street=street
            )
            results["landmark"] = LandmarkGeoSerializer(landmarks, many=True).data
                
    
        if hn:
            addresses  = self.search_address(
                hn, street=street, subdivision=subdivision, municipality=municipality, barangay=barangay
            )
            
            results["hn"] = AddressSerializer(addresses , many=True).data      
                              
        return Response({"results": results})
    
    def search_address(self, hn, street=None, subdivision=None, barangay=None, municipality=None):
        qs = Address.objects.all()

        if hn:
            qs = filter_by_hn(qs, hn)

        if street:
            street_clean = strip_suffix(street) or street
            qs = qs.annotate(street_sim=TrigramWordSimilarity(street_clean, 'street_base_name'))
            qs = qs.filter(street_sim__gt=.5)

        if barangay:
            qs = qs.annotate(brgy_sim=TrigramSimilarity('barangay', barangay))
            qs = qs.filter(brgy_sim__gt=.4)

        if municipality:
            qs = qs.annotate(city_sim=TrigramSimilarity('municipality', municipality))
            qs = qs.filter(city_sim__gt=.4)

        if subdivision:
            qs = qs.annotate(subd_sim=TrigramSimilarity('subdivision', subdivision))
            qs = qs.filter(subd_sim__gt=.5)

        return qs[:20]
    
    def search_landmark(self, landmark_query, barangay=None, city=None, street=None):
        THRESHOLD = .35
        # search landmark table and annotates the query and landmark name
        qs = Landmark.objects.annotate(
            sim=TrigramWordSimilarity(landmark_query, "name")).filter(sim__gte=.65)
        
        # self.admin_check_spatial(city, barangay, THRESHOLD, qs)
        
        if city:
            best_city_row = Admin.objects.annotate(
                sim=TrigramWordSimilarity(city, 'city')
            ).filter(sim__gte=THRESHOLD).order_by('-sim').first()
            
            if best_city_row:
                # Now get ALL barangay rows under that exact city name, and union their geometries
                city_admins = Admin.objects.filter(city=best_city_row.city)
                city_union = city_admins.aggregate(union=Union('geom'))['union']
                if city_union:
                    qs = qs.filter(geom__intersects=city_union)

        # Match barangay independently
        if barangay:
            brgy_match = Admin.objects.annotate(
                sim=TrigramWordSimilarity(barangay, 'barangay')
            ).filter(sim__gte=THRESHOLD).order_by('-sim').first()
            if brgy_match:
                qs = qs.filter(geom__intersects=brgy_match.geom)
        

        # Match street independently (unchanged from before)
        candidates = list(qs.order_by('-sim')[:20])

        if street and candidates:
            candidates = [
                lm for lm in candidates
                if find_nearby_matching_street(lm.geom, street)
            ]

        return candidates

            
        
        
