from django.contrib import admin
from .models import *

class productAdmin(admin.ModelAdmin):
    list_display = ('name','price','image1')
    
# Register your models here.

admin.site.register(customer)
admin.site.register(Category)
admin.site.register(Products)