from .models import Admin, Landmark, Road, Address
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from rest_framework import serializers
from django.contrib.gis.db.models.functions import Distance
from django.db import connection

class AdminSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Admin
        geo_field = "geom"
        fields = "__all__"

class LandmarkSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Landmark
        geo_field = "geom"
        fields = "__all__"

class RoadSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Road
        geo_field = "geom"
        fields = "__all__"

class AddressSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Address
        geo_field = "geom"
        fields = "__all__"

class LandmarkGeoSerializer(GeoFeatureModelSerializer):
    admin = serializers.SerializerMethodField()
    nearest_streets = serializers.SerializerMethodField()
    
    class Meta:
        model = Landmark
        geo_field = "geom"
        fields = ["id", "name", "admin", "nearest_streets"]
        
    def get_admin(self, obj):
        admin = Admin.objects.filter(geom__intersects=obj.geom).first()
        
        if not admin:
            return {"city": None, "barangay": None, "province": None}
        
        return {
            "city" : admin.city, 
            "barangay" : admin.barangay, 
            "province" : admin.province
        }

    # def get_nearest_streets(self, obj):
    #     roads = Road.objects.annotate(distance=Distance('geom', obj.geom)).order_by('distance')[:5]
        
    #     return [
    #         {"name": road.name, "distance_m": road.distance.m} for road in roads
    #     ]
    
    def get_nearest_streets(self, obj):
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, ST_DistanceSphere(geom, ST_GeomFromEWKB(%s)) as distance
                FROM roads
                WHERE name IS NOT NULL AND name != ''
                ORDER BY geom <-> ST_GeomFromEWKB(%s)
                LIMIT 20
            """, [bytes(obj.geom.ewkb), bytes(obj.geom.ewkb)])
            rows = cursor.fetchall()

        seen = set()
        result = []
        for name, distance in rows:
            if name in seen:
                continue
            seen.add(name)
            result.append({"name": name, "distance_m": distance})
            if len(result) == 5:
                break

        return result

