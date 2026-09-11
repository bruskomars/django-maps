from .models import Admin, Landmark, Road
from rest_framework_gis.serializers import GeoFeatureModelSerializer

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