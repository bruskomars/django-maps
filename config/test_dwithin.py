import time
from django.db import connection
from maps_backend.models import Landmark
from django.contrib.postgres.search import TrigramWordSimilarity

landmark = Landmark.objects.annotate(
    sim=TrigramWordSimilarity("Jollibee", "name")
).filter(sim__gte=.35).first()

print(landmark.name)

street_query = "Rizal"
name_threshold = 0.35
max_distance_m = 150

start = time.time()
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name, similarity(name, %s) as sim, ST_DistanceSphere(geom, %s) as distance
        FROM roads
        WHERE name IS NOT NULL AND name != ''
        AND ST_DWithin(geom::geography, %s::geography, %s)
        AND similarity(name, %s) >= %s
        ORDER BY distance ASC
        LIMIT 1
    """, [
        street_query,
        bytes(landmark.geom.ewkb),
        bytes(landmark.geom.ewkb), max_distance_m,
        street_query, name_threshold
    ])
    row = cursor.fetchone()
elapsed = time.time() - start

print(f"Took {elapsed:.4f}s")
print(f"Match: {row}")