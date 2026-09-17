# test_dwithin_debug.py
from django.db import connection
from maps_backend.models import Landmark
from django.contrib.postgres.search import TrigramWordSimilarity

landmark = Landmark.objects.annotate(
    sim=TrigramWordSimilarity("Jollibee", "name")
).filter(sim__gte=.35).first()

print("Landmark:", landmark.name)

# 1. What streets are actually near this landmark, regardless of name?
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT name, ST_DistanceSphere(geom, %s) as distance
        FROM roads
        WHERE name IS NOT NULL AND name != ''
        ORDER BY geom <-> %s
        LIMIT 10
    """, [bytes(landmark.geom.ewkb), bytes(landmark.geom.ewkb)])
    print("\nNearest streets (actual):")
    for name, dist in cursor.fetchall():
        print(f"  {name}: {dist:.1f}m")

# 2. EXPLAIN ANALYZE on the ST_DWithin query
with connection.cursor() as cursor:
    cursor.execute("""
        EXPLAIN ANALYZE
        SELECT name, similarity(name, %s) as sim, ST_DistanceSphere(geom, %s) as distance
        FROM roads
        WHERE name IS NOT NULL AND name != ''
        AND ST_DWithin(geom::geography, %s::geography, %s)
        AND similarity(name, %s) >= %s
        ORDER BY distance ASC
        LIMIT 1
    """, ["Rizal", bytes(landmark.geom.ewkb), bytes(landmark.geom.ewkb), 150, "Rizal", 0.35])
    print("\nEXPLAIN ANALYZE:")
    for row in cursor.fetchall():
        print(" ", row[0])