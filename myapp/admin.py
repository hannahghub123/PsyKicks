from django.contrib import admin
from .models import *

class productAdmin(admin.ModelAdmin):
    list_display = ('name','price','image')

class customerAdmin(admin.ModelAdmin):
    list_display = ('username','name','email','phonenumber')

class AddressAdmin(admin.ModelAdmin):
    list_display = ('address','city','country','state','zipcode')


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
admin.site.register(Coupon)
admin.site.register(Wishlist)
admin.site.register(ProductOffer)
admin.site.register(CategoryOffer)
admin.site.register(Productvariant)
admin.site.register(Wallet)
