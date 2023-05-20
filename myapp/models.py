from django.db import models

# Create your models here.

class customer(models.Model):
    username = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phonenumber = models.IntegerField()
    password = models.CharField(max_length=200)
    isblocked = models.BooleanField(default=False)

class category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    stock = models.IntegerField()
    isblocked = models.BooleanField(default=False)

class product(models.Model):
    productname = models.CharField(max_length=200, unique=True)
    description = models.TextField(blank=True)
    quantity = models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(category, on_delete=models.CASCADE)







