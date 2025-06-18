# Module: models.py

from django.contrib.auth.models import User
from django.db import models

class Advocate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    enrollment_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name or str(self.user)

class Client(models.Model):
    client_name = models.CharField(max_length=100, blank=True, null=True)
    filer = models.CharField(max_length=50, blank=True, null=True)
    husband_name = models.CharField(max_length=50, blank=True, null=True)
    husband_address = models.TextField(max_length=200, blank=True, null=True)
    wife_name = models.CharField(max_length=50, blank=True, null=True)
    wife_address = models.TextField(max_length=200, blank=True, null=True)
    marriage_Date = models.DateField(blank=True, null=True)  # Changed to DateField for consistency
    Date = models.DateField(auto_now_add=True)
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, related_name='clients', blank=True, null=True)
    reason = models.TextField(max_length=1000, blank=True, null=True)
    document_version_1 = models.FileField(upload_to='documents/', null=True, blank=True)
    document_version_2 = models.FileField(upload_to='documents/', null=True, blank=True)

    def __str__(self):
        return self.client_name or ''


class NDA_Details(models.Model):
    # Add these fields:
    advocate = models.ForeignKey('Advocate', on_delete=models.CASCADE, related_name="nda_details",null=True)
    client_name = models.CharField(max_length=255,null=True)  # Receiving party name usually

    # Existing fields (as is):
    disclosing_party_name = models.CharField(max_length=255, blank=True, null=True)
    disclosing_party_representative = models.CharField(max_length=255, blank=True, null=True)
    disclosing_party_title = models.CharField(max_length=255, blank=True, null=True)
    disclosing_party_address = models.TextField(max_length=200, blank=True, null=True)
    receiving_party_name = models.CharField(max_length=255, blank=True, null=True)
    receiving_party_representative = models.CharField(max_length=255, blank=True, null=True)
    receiving_party_title = models.CharField(max_length=255, blank=True, null=True)
    receiving_party_address = models.TextField(max_length=255, blank=True, null=True)
    effective_date = models.DateField(blank=True, null=True)
    duration = models.PositiveSmallIntegerField(help_text='Duration in years')
    definition_confidential_information = models.TextField(max_length=1000)
    non_competition = models.BooleanField(default=False)
    non_competition_duration = models.PositiveSmallIntegerField(blank=True, null=True, help_text='Non-competition duration in years')
    non_circumvention = models.BooleanField(default=False)
    intellectual_property_rights = models.TextField(blank=True, null=True)
    data_destruction_policy = models.TextField(blank=True, null=True)
    penalties = models.TextField(blank=True, null=True)
    jurisdiction = models.TextField(blank=True, null=True)
    dispute_resolution_method = models.TextField(blank=True, null=True)

    # For document versions:
    document_version_1 = models.FileField(upload_to="nda_docs/", blank=True, null=True)
    document_version_2 = models.FileField(upload_to="nda_docs/", blank=True, null=True)

    created_at = models.DateTimeField(null=True, blank=True)


    def __str__(self):
        return f'NDA between {self.disclosing_party_name} and {self.receiving_party_name}'

