from django.contrib.gis import admin
from .models import Admin, Landmark, Road, Address
# Register your models here.
class CustomGeoAdmin(admin.GISModelAdmin):
    gis_widget_kwargs = {
        'attrs':{
            'default_zoom': 14,
            'default_lon': 121.037281,
            'default_lat': 14.569973,
        }
    }
    
@admin.register(Admin)
class AdminAdmin(CustomGeoAdmin):
    pass

@admin.register(Landmark)
class LandmarkAdmin(CustomGeoAdmin):
    pass

@admin.register(Road)
class RoadAdmin(CustomGeoAdmin):
    pass

@admin.register(Address)
class AddressAdmin(CustomGeoAdmin):
    pass