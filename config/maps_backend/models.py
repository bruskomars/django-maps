# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.contrib.gis.db import models


class Admin(models.Model):
    id = models.BigIntegerField(primary_key=True)
    geom = models.MultiPolygonField(blank=True, null=True)
    province = models.CharField(max_length=240, blank=True, null=True, db_column='name1')
    city = models.CharField(max_length=240, blank=True, null=True, db_column='name2')
    barangay = models.CharField(max_length=240, blank=True, null=True, db_column='name3')
    postcode = models.CharField(max_length=10, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'admin'
        verbose_name_plural = 'admins'
        
    
    def __str__(self):
        return self.city  # or any other field you want to use as the string representation


class Landmark(models.Model):
    id = models.BigIntegerField(primary_key=True)
    geom = models.PointField(blank=True, null=True)
    name = models.CharField(max_length=240, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'landmark'
        verbose_name_plural = 'landmarks'
    
    def __str__(self):
        return self.name  # or any other field you want to use as the string representation


class Road(models.Model):
    id = models.BigIntegerField(primary_key=True, db_column='objectid')
    geom = models.MultiLineStringField(blank=True, null=True)
    rdlnclass = models.BigIntegerField(blank=True, null=True)
    name = models.CharField(max_length=240, blank=True, null=True)
    name_pf = models.CharField(max_length=90, blank=True, null=True)
    name_sf = models.CharField(max_length=90, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'roads'
        verbose_name_plural = 'roads'
    
    def __str__(self):
        return self.name or f"Unnamed Road - {self.pk}" # or any other field you want to use as the string representation
