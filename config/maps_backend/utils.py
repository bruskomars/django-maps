from django.db import connection
import re
from django.db.models import Value, CharField
from django.db.models.functions import Replace


def find_nearby_matching_street(geom, street_query, name_threshold=0.35, k=20, max_distance_m=150):
        """
        Check whether a street matching `street_query` exists within `max_distance_m`
        of this landmark, regardless of its rank among nearby streets.
        Uses the fast index-accelerated KNN operator to fetch candidates,
        then filters by distance + name similarity in Python.
        """
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT name, similarity(name, %s) as sim, ST_DistanceSphere(geom, %s) as distance
                FROM roads
                WHERE name IS NOT NULL AND name != ''
                ORDER BY geom <-> %s
                LIMIT %s
            """, [street_query, bytes(geom.ewkb), bytes(geom.ewkb), k])
            rows = cursor.fetchall()

        return any(
            distance <= max_distance_m and sim >= name_threshold
            for name, sim, distance in rows
        )

def filter_by_hn(queryset, hn):
    """
    Filter a queryset by house number (exact match, allowing a letter suffix
    but rejecting numeric continuations — e.g. "145" matches "145A" but not "1450").
    Extracted from AddressListView's original inline logic.
    """
    def normalize_hn(value):
        return value.replace(' ', '').replace('-', '')

    hn_normalized = normalize_hn(hn)
    escaped = re.escape(hn_normalized)
    pattern = rf'^{escaped}$|^{escaped}[^0-9]'

    return queryset.annotate(
        hn_normalized=Replace(
            Replace('hn', Value(' '), Value(''), output_field=CharField()),
            Value('-'), Value(''), output_field=CharField()
        )
    ).filter(hn_normalized__iregex=pattern)


STREET_SUFFIXES = r'\b(street|st\.?|avenue|ave\.?|avenida|road|rd\.?|boulevard|blvd\.?|drive|dr\.?|lane|ln\.?|calle)\b'


def strip_suffix(value):
    cleaned = re.sub(STREET_SUFFIXES, '', value, flags=re.IGNORECASE)
    cleaned = re.sub(r'\s+', ' ', cleaned).strip()
    return cleaned