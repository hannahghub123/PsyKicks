from django.contrib import admin
from .models import *

class productAdmin(admin.ModelAdmin):
    list_display = ('name','price','image')
    
# Register your models here.

admin.site.register(customer)
admin.site.register(Category)
admin.site.register(Color)
admin.site.register(Size)
admin.site.register(Brand)
admin.site.register(Gender)
admin.site.register(Products)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(ShippingAddress)
admin.site.register(Cart)
admin.site.register(ProductImage)
