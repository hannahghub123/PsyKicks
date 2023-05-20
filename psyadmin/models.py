from django.db import models

# Create your models here.
class myadmin(models.Model):
    adminuser = models.CharField(max_length=300)
    adminpass = models.CharField(max_length=300)
