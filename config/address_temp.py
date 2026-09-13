# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class Address(models.Model):
    id = models.IntegerField(primary_key=True)
    geom = models.PointField(blank=True, null=True)
    country_code = models.CharField(blank=True, null=True)
    geometry = models.CharField(blank=True, null=True)
    municipality = models.CharField(blank=True, null=True)
    barangay = models.CharField(blank=True, null=True)
    postal_code = models.CharField(blank=True, null=True)
    street_base_name = models.CharField(blank=True, null=True)
    house_number = models.CharField(blank=True, null=True)
    block_number = models.CharField(blank=True, null=True)
    lot_number = models.CharField(blank=True, null=True)
    building_name = models.CharField(blank=True, null=True)
    street_pf_name = models.CharField(blank=True, null=True)
    street_sf_name = models.CharField(blank=True, null=True)
    street_unique_criteria_type = models.CharField(blank=True, null=True)
    street_unique_criteria_name = models.CharField(blank=True, null=True)
    unique_street_name = models.CharField(blank=True, null=True)
    subdivision = models.CharField(blank=True, null=True)
    province = models.CharField(blank=True, null=True)
    region = models.CharField(blank=True, null=True)
    creat_dt = models.DateField(blank=True, null=True)
    updtd_dt = models.DateField(blank=True, null=True)
    revw_dt = models.DateField(blank=True, null=True)
    srce_ath = models.CharField(blank=True, null=True)
    old = models.CharField(max_length=20, blank=True, null=True)
    new = models.CharField(max_length=20, blank=True, null=True)
    int_field = models.CharField(db_column='int_', max_length=1, blank=True, null=True)  # Field renamed because it ended with '_'.
    admin_id = models.CharField(max_length=12, blank=True, null=True)
    source = models.CharField(max_length=10, blank=True, null=True)
    batch = models.CharField(max_length=10, blank=True, null=True)
    link_id = models.FloatField(blank=True, null=True)
    rap = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'address'
