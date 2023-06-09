from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from myapp.models import *
import os

@never_cache
def admin_index(request):
    if 'adminuser' in request.session:
        return render(request, "psyadmin/admin-index.html")
    else:
        return redirect('admin_login')

@never_cache 
def admin_login(request):
    if 'adminuser' in request.session:
        return redirect('admin_index')
    
    if request.method == 'POST':
        adminuser = request.POST['adminuser']
        adminpass = request.POST['adminpass']

        user = authenticate( username=adminuser, password=adminpass)
        
        if user is not None:
            # login(request, user)
            request.session['adminuser'] = adminuser
            return redirect('admin_index')
        else:
            error_message = 'Invalid username or password!'
            return render(request,"psyadmin/admin-login.html",{"error_message":error_message})

    
    return render(request, 'psyadmin/admin-login.html')

@never_cache
def admin_logout(request):
    if 'adminuser' in request.session:
        del request.session['adminuser']
    return redirect('admin_login')

@never_cache
def products(request):
    if "adminuser" in request.session:
        datas=Products.objects.all()

        if request.method=="POST":
            enteredproduct=request.POST.get("searchitem")
            datas=Products.objects.filter(name=enteredproduct)
            return render(request,"psyadmin/products.html",{"datas":datas})
        
        return render(request,"psyadmin/products.html",{"datas":datas})
    else:
        return redirect(admin_login)
    

from django.shortcuts import get_object_or_404

def addproducts(request):
    error_message = {}
    categoryobjs = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    brands = Brand.objects.all()
    genders = Gender.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        category_name = request.POST.get("category")
        color_names = request.POST.getlist("color")
        gender_name = request.POST.get("gender")
        size_names = request.POST.getlist("size")
        
        brand_name = request.POST.get("brand")
        description = request.POST.get("description")
        images = request.FILES.getlist("image")

        if len(name) < 4:
            error_message["name"] = "Product name should contain a minimum of four characters."
        elif len(name) > 20:
            error_message["name"] = "Product name can only have up to 20 characters."
        elif not all(c.isalnum() or c.isspace() for c in name):
            error_message["name"] = "Invalid string entry for product name."
      

        if Products.objects.filter(name__iexact=name.replace(" ", "")).exists():
            error_message["name"] = "A product with a similar name already exists."
        elif not price.isdigit():
            error_message["price"] = "Price should be a numeric value."
        elif not quantity.isdigit():
            error_message["quantity"] = "Quantity should be a numeric value."
        elif not Category.objects.filter(name=category_name).exists():
            error_message["category"] = "Invalid category."

        if error_message:
            return render(request, "psyadmin/add-products.html", {
                "error_message": error_message,
                "categoryobjs": categoryobjs,
                "colors": colors,
                "sizes": sizes,
                "brands": brands,
                "genders": genders
            })

        category_object = Category.objects.get(name=category_name)
        gender_instance = get_object_or_404(Gender, name=gender_name)
        brand_instance = get_object_or_404(Brand, name=brand_name)
        

        product = Products(
            name=name,
            price=price,
            quantity=quantity,
            category=category_object,
            gender=gender_instance,
            brand=brand_instance,
            description=description
        )
        product.save()
        

        
        # Get the Color objects based on the color names
        color_objects = Color.objects.filter(name__in=color_names)
        product.color.set(color_objects)  # Set the colors using the set() method

        size_objects = Size.objects.filter(name__in=size_names)
        product.size.set(size_objects) 
        
        
        for image in images:
            ProductImage.objects.create(product=product, image=image)
        
        return redirect("products")

    return render(request, "psyadmin/add-products.html", {
        "categoryobjs": categoryobjs,
        "colors": colors,
        "sizes": sizes,
        "brands": brands,
        "genders": genders
    })


def editproducts(request, someid):
    content = Products.objects.get(id=someid)
    categoryobjs = Category.objects.all()
    colors = Color.objects.all()
    genders = Gender.objects.all()
    sizes = Size.objects.all()
    brands = Brand.objects.all()
    images = ProductImage.objects.filter(product=content)
    error_message={}

    if request.method == 'POST':
        # Validate form inputs
        name = request.POST.get("name")
        price = request.POST.get("price")
        quantity = request.POST.get("quantity")
        category_name = request.POST.get("category")
        description = request.POST.get("description")

        if len(name) < 4:
            error_message["name"] = "Product name should contain a minimum of four characters"
        if len(name) > 20:
            error_message["name"]  = "Product name can only have up to 20 characters"
        if not name.isalpha():
            error_message["name"]  = "Product name can't contain numbers"
        if Products.objects.filter(name__iexact=name.replace(" ", "")).exists():
            error_message["name"]  = "A product with a similar name already exists"
        if not price.isnumeric():
            error_message["price"]  = "Price should be a valid number"
        if not quantity.isnumeric():
            error_message["quantity"]  = "Quantity should be a valid number"
        if len(description) < 4:
            error_message["description"]  = "Description should contain a minimum of four characters"
        if  error_message:
            return render(request, "psyadmin/edit-products.html",{ 'content': content,'categoryobjs': categoryobjs,'colors': colors,'genders': genders,'sizes': sizes,'brands': brands,'images': images,'error_message':error_message} )

        else:
            content.name = name
            content.description = description
            content.price = price
            content.quantity = quantity

            # Retrieve the category if it exists, otherwise assign a default category
            categoryobject = Category.objects.get(name=category_name)
            content.category = categoryobject

            # Update color, gender, size, and brand
            color_ids = request.POST.getlist("color")
            content.color.set(color_ids)

            gender_id = request.POST.get("gender")
            content.gender = Gender.objects.get(id=gender_id) if gender_id else None

            size_ids = request.POST.getlist("size")
            content.size.set(size_ids)

            brand_id = request.POST.get("brand")
            content.brand = Brand.objects.get(id=brand_id) if brand_id else None

            # Check if new images are provided
            if 'image' in request.FILES:
                # Delete the existing images
                for image in images:
                    os.remove(image.image.path)
                    image.delete()

                # Save new images
                for image_file in request.FILES.getlist('image'):
                    ProductImage.objects.create(product=content, image=image_file)

            content.save()
            return redirect('products')

    context = {
        'content': content,
        'categoryobjs': categoryobjs,
        'colors': colors,
        'genders': genders,
        'sizes': sizes,
        'brands': brands,
        'images': images,
      
    }

    return render(request, "psyadmin/edit-products.html", context)


def deleteproducts(request, someid):
    content = get_object_or_404(Products, id=someid)

    # Delete the product
    content.delete()

    # Redirect to a specific URL or view
    return redirect('products') 

@never_cache
def categories(request):
    if "adminuser" in request.session:
        datas=Category.objects.all()
        return render(request,"psyadmin/categories.html",{"datas":datas})
    else:
        return redirect(admin_login)


def addcategories(request):
    datas = Category.objects.all()
    error_message = {}

    if request.method == "POST":
        name = request.POST.get("name")
        stock = request.POST.get("stock")

        if len(name) == 0:
            error_message["name"] = "Category name field can't be empty"
        elif not name.isalpha():
            error_message["name"] = "Category name can't contain numbers"
        elif len(name) < 4:
            error_message["name"] = "Category name should have at least 4 letters"
        elif len(name) > 20:
            error_message["name"] = "Category name can have at most 20 letters"
        elif Category.objects.filter(name__iexact=name.replace(" ", "")).exists():
            error_message["name"] = "Category already exists!!"

        if error_message:
            return render(request, "psyadmin/addcategories.html", {"datas": datas, "error_message": error_message})
        else:
            category = Category(name=name)
            category.save()
            return redirect('categories')

    return render(request, "psyadmin/addcategories.html", {"datas": datas, "error_message": error_message})



def editcategories(request,someid):
    obj=Category.objects.get(id=someid)
    categoryobjs=Category.objects.all()

    if request.method=="POST":
        name=request.POST.get("name")
        stock=request.POST.get("stock")

        if len(name)==0:
            error="Category name field can't be empty"
        elif name.isalpha()==False:
            error="Category name can't be numbers"
        elif len(name)<3:
            error="Category name should atleast have 4 letters"
        elif Category.objects.filter(name=name):
            error="Same Category name is not allowed"
        elif len(name)>20:
            error="Category name atmost can have only 20 letters"
        else:
            obj.name=name
            obj.stock=stock
           
            edited = Category(id=someid, name=name, stock=stock)
            edited.save()
           
            return redirect(categories)
        if error:
            return render(request,"psyadmin/editcategories.html",{"obj":obj,"error":error,"categoryobjs":categoryobjs})

    return render(request,"psyadmin/editcategories.html",{"obj":obj,"categoryobjs":categoryobjs})

def deletecategories(request, someid):
    content = get_object_or_404(Category, id=someid)

    # Delete the category
    content.delete()

    # Redirect to a specific URL or view
    return redirect('categories') 

@never_cache
def users(request):
    if "adminuser" in request.session:
        datas=customer.objects.all()
        # if request.method=="POST":
        #     username=request.POST.get("searchitem")
        #     datas=customer.objects.filter(username=username)
        #     return render(request,"psyadmin/users.html",{"datas":datas})
        return render(request,"psyadmin/users.html",{"datas":datas})
    else:
        return redirect(admin_login)

def blockuser(request,someid):
    obj=customer.objects.get(id=someid)
    obj.isblocked=True
    obj.save()
    return redirect(users)

def unblockuser(request,someid):
    obj=customer.objects.get(id=someid)
    obj.isblocked=False
    obj.save()
    return redirect(users)

def blockcategory(request,someid):
    obj=Category.objects.get(id=someid)
    obj.isblocked=True
    obj.save()
    return redirect(categories)

def unblockcategory(request,someid):
    obj=Category.objects.get(id=someid)
    obj.isblocked=False
    obj.save()
    return redirect(categories)

def orders(request):
    if "adminuser" in request.session:
        datas = Order.objects.select_related('cart__product').prefetch_related('cart__product__images').all()

       

        return render(request,"psyadmin/orders.html",{"datas":datas})
    else:
        return redirect(admin_login)
    


def coupon_management(request):
    if 'adminuser' in request.session:
        datas = Coupon.objects.all()
        return render(request, "psyadmin/coupon-management.html", {"datas": datas})
    else:
        # Handle the case where the user is not authenticated as an admin
        return redirect('login')  # Replace 'login' with the appropriate URL name

def add_coupon(request):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    if request.method == "POST":
        coupon_code = request.POST.get("couponcode")
        discount_price = request.POST.get("discountprice")
        minimum_amount = request.POST.get("minimum_amount")

        error_message = {}

        if not coupon_code:
            error_message["coupon_code"] = "Coupon code field can't be empty"

        if not discount_price:
            error_message["discount_price"] = "Discount price field can't be empty"

        if not minimum_amount:
            error_message["minimum_amount"] = "Minimum amount field can't be empty"

        if Coupon.objects.filter(coupon_code=coupon_code).exists():
            error_message["coupon_code"] = "Coupon code already exists"

        if error_message:
            datas = Coupon.objects.all()
            return render(request, "psyadmin/add-coupon.html", {"datas": datas, "error_message": error_message})

        coupon = Coupon(coupon_code=coupon_code, discount_price=discount_price, minimum_amount=minimum_amount)
        coupon.save()

        return redirect('coupon_management')  # Replace 'coupon_management' with the appropriate URL name

    datas = Coupon.objects.all()
    error_message = {}
    return render(request, "psyadmin/add-coupon.html", {"datas": datas, "error_message": error_message})

def is_expired(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = Coupon.objects.get(id=someid)
        obj.is_expired = True
        obj.save()
    except Coupon.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('coupon_management')  # Replace 'coupon_management' with the appropriate URL name

def available(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = Coupon.objects.get(id=someid)
        obj.is_expired = False
        obj.save()
    except Coupon.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('coupon_management')  # Replace 'coupon_management' with the appropriate URL name







