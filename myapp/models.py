from django.db import models

# Create your models here.

class customer(models.Model):
    username = models.CharField(max_length=200, unique=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phonenumber = models.IntegerField()
    password = models.CharField(max_length=200)
    isblocked = models.BooleanField(default=False)
    is_verified = models.BooleanField(default=False)
    verification_code = models.CharField(max_length=6,  default='') 

    def __str__(self):
        return self.name

class Category(models.Model):
    name = models.CharField(max_length=200, unique=True)
    isblocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Color(models.Model):
    name = models.CharField(max_length=200, unique=True)
    isblocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Gender(models.Model):
    name = models.CharField(max_length=200, unique=True)
    isblocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Size(models.Model):
    name = models.CharField(max_length=200, unique=True)
    isblocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Brand(models.Model):
    name = models.CharField(max_length=200, unique=True)
    isblocked = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class Products(models.Model):
    name = models.CharField(max_length=200, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    color = models.ManyToManyField(Color)
    gender = models.ForeignKey(Gender, on_delete=models.CASCADE, default=None, null=True)
    size = models.ManyToManyField(Size)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default=None, null=True)
    description = models.TextField(blank=True)
    digital = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=True, blank=True, related_name='images', default=None)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.image.name

class Cart(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)

    
class Order(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.SET_NULL, null=True, blank=True) 
    cart=models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True)
    date_ordered = models.DateTimeField(auto_now_add=True)
    complete = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=100, null=True)

    def __str__(self):
        return str(self.id)
    
    
    
    @property
    def get_cart_total(self):
        orderItems = self.orderitem_set.all()
        total = sum([item.get_total for item in orderItems])
        return total
    
    @property
    def get_cart_items(self):
        orderItems = self.orderitem_set.all()
        total = sum([item.quantity for item in orderItems])
        return total
    

    
class OrderItem(models.Model):
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, blank=True, null=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    quantity = models.IntegerField(default=0, null=True, blank=True)
    date_added = models.DateTimeField(auto_now_add=True)

    @property
    def get_total(self):
        total = self.product.price * self.quantity
        return total

class ShippingAddress(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey(Order, on_delete=models.SET_NULL, blank=True, null=True)
    address = models.CharField(max_length=100, null=True)
    city = models.CharField(max_length=100, null=True)
    country = models.CharField(max_length=100, null=True)
    state = models.CharField(max_length=100, null=True)
    zipcode = models.CharField(max_length=100, null=True)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.address
    







