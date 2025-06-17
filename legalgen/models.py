# Module: models.py

# Import Necessary Liberies
from django.contrib.auth.models import User
from django.db import models

class Advocate(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    enrollment_number = models.CharField(max_length=50, unique=True, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    address = models.CharField(max_length=100,blank=True,null=True)

    def __str__(self):
        return self.name or self.user

class Client(models.Model):
    client_name = models.CharField(max_length=100, blank=True, null=True)
    filer = models.CharField(max_length=50, blank=True, null=True)
    husband_name = models.CharField(max_length=50, blank=True, null=True)
    husband_address = models.TextField(max_length=200, blank=True, null=True)
    wife_name = models.CharField(max_length=50, blank=True, null=True)
    wife_address = models.TextField(max_length=200, blank=True, null=True)
    marriage_Date = models.DateTimeField(blank=True, null=True)
    Date = models.DateField(auto_now_add=True)
    advocate = models.ForeignKey(Advocate, on_delete=models.CASCADE, related_name='clients', blank=True, null=True)
    reason = models.TextField(max_length=1000,blank=True, null=True)
    document_version_1 = models.FileField(upload_to='documents/', null=True, blank=True)
    document_version_2 = models.FileField(upload_to='documents/', null=True, blank=True)


    def __str__(self):
        return self.client_name or '' 
    



