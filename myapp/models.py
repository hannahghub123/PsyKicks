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
    category = models.ForeignKey(Category, on_delete=models.CASCADE)   
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, default=None, null=True)
    digital = models.BooleanField(default=False)

    def __str__(self):
        return self.name
    
class Productvariant(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=True, blank=True, default=None)
    # gender = models.ForeignKey(Gender, on_delete=models.CASCADE, default=None, null=True)
    color = models.ManyToManyField(Color)
    size = models.ManyToManyField(Size)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    # image = models.ImageField(upload_to='products/', null=True, blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return f"Variant #{self.id} - {self.product}"

class ProductImage(models.Model):
    product = models.ForeignKey(Products, on_delete=models.CASCADE,null=True, blank=True, related_name='images', default=None)
    # variant = models.ForeignKey(Productvariant, on_delete=models.CASCADE,null=True, blank=True, related_name='images', default=None)
    image = models.ImageField(upload_to='products/', null=True, blank=True)

    def __str__(self):
        return self.image.name

class Coupon(models.Model):
    coupon_code = models.CharField(max_length=50)
    is_expired = models.BooleanField(default=False)
    discount_price = models.IntegerField(default=100)
    minimum_amount = models.IntegerField(default=500)


class Cart(models.Model):
    user = models.ForeignKey(customer, on_delete=models.CASCADE)
    # product = models.ForeignKey(Products, on_delete=models.CASCADE)
    variant= models.ForeignKey(Productvariant,on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    total = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey(Coupon,on_delete=models.SET_NULL,null=True, blank=True)

    
class Order(models.Model):
    ORDER_STATUS_CHOICES = (
        ('order_pending', 'Order_Pending'),
        ('order_confirmed', 'Order_Confirmed'),
        ('delivered', 'Delivered'),
        ('returned', 'Returned'),
        ('cancelled', 'Cancelled'),
    )

    PAYMENT_CHOICES = (
        ('cash_on_delivery', 'Cash_on_Delivery'),
        ('online_payment', 'Online_payment'),
    )
    # order_id = models.AutoField(primary_key=True)
    customer = models.ForeignKey(customer, on_delete=models.SET_NULL, null=True, blank=True) 
    date_ordered = models.DateTimeField(auto_now_add=True)
    order_status = models.CharField(max_length=100,choices=ORDER_STATUS_CHOICES,
        default='order_pending')
    payment_type = models.CharField(max_length=100,choices=PAYMENT_CHOICES,default="Cash on delivery")
    # discount is to store the discount amount applied
    discount = models.DecimalField(max_digits=10, decimal_places=2,default=0) 
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)

    # def __str__(self):
    #     return str(self.id)

    def __str__(self):
        return f"Order #{self.id} - {self.order_status}"
    
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
    price = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2,default=0)
    date_added = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"OrderItem #{self.id}"

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
    
class Wishlist(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)

class ProductOffer(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    offercode = models.CharField(max_length=50)
    discount = models.IntegerField(default=0, null=True, blank=True)
    is_expired = models.BooleanField(default=False)


class CategoryOffer(models.Model):
    customer = models.ForeignKey(customer, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    offercode = models.CharField(max_length=50)
    discount = models.IntegerField(default=0, null=True, blank=True)
    is_expired = models.BooleanField(default=False)


