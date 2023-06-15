from urllib import request
from django.shortcuts import get_object_or_404, render, redirect
from django.views.decorators.cache import never_cache
from django.contrib.auth import authenticate, login
from myapp.models import *
import os
from django.http import HttpResponse

from django.db import models
from django.shortcuts import render, redirect
from django.http import FileResponse
from django.utils.html import format_html
from django.contrib import messages
from django.utils import timezone
from datetime import datetime
from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib import colors
import xlsxwriter


import io
from datetime import datetime
from django.http import FileResponse




@never_cache
def admin_index(request):
    if 'adminuser' in request.session:
        orderobjs=OrderItem.objects.all()
        top_returned_product=None
        top_product=None

        orderdict={}
        for item in orderobjs:
            if item.variant.product.name not in orderdict:
                orderdict[item.variant.product.name]=item.quantity
            else:
                orderdict[item.variant.product.name]+=item.quantity
        try:
            top_count = max(orderdict.values())
        except:
            pass
        for key,value in orderdict.items():
            if value==top_count:
                top_product=key
                break
        
        #Most Returned Products Graph logic
        returninitiatedobjs = OrderItem.objects.filter(order__order_status='returned')

        returndict={}
        for i in returninitiatedobjs:
            if i.product.name not in returndict:
                returndict[i.product.name]=1
            else:
                returndict[i.product.name]+=1
        try:
            top_returned_count=max(returndict.values())
        except:
            pass

        for key,value in returndict.items():
            if value==top_returned_count:
                top_returned_product=key

        return render(request, "psyadmin/admin-index.html",{"orderdict":orderdict,"returndict":returndict,"top_product":top_product,"top_count":top_count,"top_returned_product":top_returned_product})
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

        if request.method == "POST":
            entered_product = request.POST.get("searchitem")
            datas = Products.objects.filter(name__icontains=entered_product)
            return render(request, "psyadmin/products.html", {"datas": datas})

        
        return render(request,"psyadmin/products.html",{"datas":datas})
    else:
        return redirect(admin_login)


def productvariant(request,item_id):
    try:

        pobj = Products.objects.get(id=item_id)
        variant = Productvariant.objects.filter(product=pobj)
   

        context={
            "variant":variant,
            "pobj":pobj,
            "item_id":item_id
        }
        return render(request,"psyadmin/productvariant.html",context)
    except:
        return redirect(products)


from django.shortcuts import get_object_or_404

def addproducts(request):
    error_message = {}
    categoryobjs = Category.objects.all()
    brands = Brand.objects.all()

    if request.method == "POST":
        name = request.POST.get("name")
        brand_name = request.POST.get("brand")
        category_name = request.POST.get("category")
        images = request.FILES.getlist("image")
        product = Products.objects.filter(name=name)

        category_object = Category.objects.get(name=category_name)
        brand_instance = get_object_or_404(Brand, name=brand_name)
        
        if len(name) < 4:
            error_message["name"] = "Product name should contain a minimum of four characters."
        elif len(name) > 20:
            error_message["name"] = "Product name can only have up to 20 characters."
        elif not all(c.isalnum() or c.isspace() for c in name):
            error_message["name"] = "Invalid string entry for product name."
        elif Products.objects.filter(name__iexact=name.replace(" ", "")).exists():
            error_message["name"] = "A product with a similar name already exists."
        elif not Category.objects.filter(name=category_name).exists():
            error_message["category"] = "Invalid category."

        if error_message:
            return render(request, "psyadmin/add-products.html", {
                "error_message": error_message,
                "categoryobjs": categoryobjs,
                "images":images,
                "brand":brand_instance,
               
            })

        product = Products(
            name=name,
            category=category_object,
            brand=brand_instance,
        )
        product.save()

        for image in images:
                product_image = ProductImage(product=product, image=image)
                product_image.save()

           
        
        return redirect("products")

    return render(request, "psyadmin/add-products.html", {
        "categoryobjs": categoryobjs,
        "brands": brands,
    })



def addvariant(request,item_id):
    error_message = {}
    colors = Color.objects.all()
    sizes = Size.objects.all()
    pobj=Products.objects.get(id=item_id)
    product = Productvariant.objects.filter(product=pobj).first()
    variant=Productvariant.objects.filter(id=item_id)
    

    if request.method == "POST":
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        color_names = request.POST.getlist("color")
        
        size_names = request.POST.getlist("size")
        description = request.POST.get("description")
        images = request.FILES.getlist("image")

        color_ids = [Color.objects.get(name=color_name).id for color_name in color_names]
        size_ids = [Size.objects.get(name=size_name).id for size_name in size_names]


        if not price.isdigit():
                error_message["price"] = "Price should be a numeric value."
        elif not stock.isdigit():
            error_message["stock"] = "Stock should be a numeric value."

      
        if Productvariant.objects.filter(
            product=pobj,
           
            color__id__in=color_ids,
            size__id__in=size_ids
        ).exists():
            error_message["name"] = "Variant already exists"


        if error_message:
            return render(request, "psyadmin/add-productvariant.html", {
                "error_message": error_message,
                "pobj":pobj,
                "colors": colors,
                "sizes": sizes,               
                'description':description,
                'price':price,
                'stock':stock,

            })

              

        variant = Productvariant(
            product=pobj,
            price=price,
            stock=stock,       
            description=description,
        )
        variant.save()
        
        color_name = color_names[0]  
        color_object = Color.objects.get(name=color_name)
        variant.color.set([color_object]) 
        size_name = size_names[0]
        size_object = Size.objects.get(name=size_name)
        variant.size.set([size_object])

        variant.save()

        # for image in images:
        #         product_image = ProductImage(product=pobj, image=image)
        #         product_image.save()

            
        return redirect("productvariant",item_id=item_id)

    return render(request, "psyadmin/add-productvariant.html", {
        "colors": colors,
        "sizes": sizes,    
        "variant":variant,
        "item_id":item_id,
        "pobj":pobj,
        'price':price,
        'stock':stock, 'description':description,
    })
 


def editvariant(request,item_id):
    variant = Productvariant.objects.get(id=item_id)
    product=variant.product
    productid=product.id
    # product = Products.objects.filter(id=item_id)
    # pobj=Products.objects.get(id=item_id)
    # categoryobjs = Category.objects.all()
    colors = Color.objects.all()
    sizes = Size.objects.all()
    brands = Brand.objects.all()
    
    error_message={}

    if request.method == 'POST':
        # Validate form inputs
        # name = request.POST.get("name")
        price = request.POST.get("price")
        stock = request.POST.get("stock")
        # category_name = request.POST.get("category")
        description = request.POST.get("description")

        # if len(name) < 4:
        #     error_message["name"] = "Product name should contain a minimum of four characters"
        # if len(name) > 20:
        #     error_message["name"]  = "Product name can only have up to 20 characters"
        # if not name.isalpha():
        #     error_message["name"]  = "Product name can't contain numbers"
        # if Products.objects.filter(name__iexact=name.replace(" ", "")).exists():
        #     error_message["name"]  = "A product with a similar name already exists"
        if not price.isnumeric():
            error_message["price"]  = "Price should be a valid number"
        if not stock.isnumeric():
            error_message["quantity"]  = "Quantity should be a valid number"
        if len(description) < 4:
            error_message["description"]  = "Description should contain a minimum of four characters"
        if  error_message:
            return render(request, "psyadmin/edit-productvariant.html",{
                 'variant': variant,
                #  'categoryobjs': categoryobjs,
                 'colors': colors,
                 'sizes': sizes,'brands': brands,
                #  'images': images,
                 'error_message':error_message} )

        else:
            # variant.name = name
            variant.description = description
            variant.price = price
            variant.stock = stock

            # Retrieve the category if it exists, otherwise assign a default category
            # categoryobject = Category.objects.get(name=category_name)
            # content.category = categoryobject

            # Update color, size, and brand
            color_ids = request.POST.getlist("color")
            variant.color.set(color_ids)
            size_ids = request.POST.getlist("size")
            variant.size.set(size_ids)
            brand_id = request.POST.get("brand")
            variant.brand = Brand.objects.get(id=brand_id) if brand_id else None


            variant.save()
            # return redirect('productvariant',item_id=item_id)
            context = {
            'variant': variant,
            'product':product,
            # 'categoryobjs': categoryobjs,
            'colors': colors,
       
            'sizes': sizes,
            'brands': brands,
            # 'images': images,
            "success":"Updated successfuly"
        
            }
            # return render(request, "psyadmin/edit-productvariant.html", context)
            return redirect(productvariant,productid)

    context = {
        'variant': variant,
        'product':product,
        # 'categoryobjs': categoryobjs,
        'colors': colors,
  
        'sizes': sizes,
        'brands': brands,
        # 'images': images,
      
    }

    return render(request, "psyadmin/edit-productvariant.html", context)



def editproducts(request, someid):
    content = Products.objects.get(id=someid)
    categoryobjs = Category.objects.all()
    brands = Brand.objects.all()
    images = ProductImage.objects.filter(product=content)

    error_message={}

    if request.method == 'POST':
        # Validate form inputs
        name = request.POST.get("name")
        # price = request.POST.get("price")
        # quantity = request.POST.get("quantity")
        category_name = request.POST.get("category")
        # description = request.POST.get("description")

        # if 'delete_selected' in request.POST:
        #     selected_images = request.POST.getlist('delete_images')

        if len(name) < 4:
            error_message["name"] = "Product name should contain a minimum of four characters"
        if len(name) > 20:
            error_message["name"]  = "Product name can only have up to 20 characters"
        if not name.isalpha():
            error_message["name"]  = "Product name can't contain numbers"
        # if Products.objects.filter(name__iexact=name.replace(" ", "")).exists():
        #     error_message["name"]  = "A product with a similar name already exists"
        # if not price.isnumeric():
        #     error_message["price"]  = "Price should be a valid number"
        # if not quantity.isnumeric():
        #     error_message["quantity"]  = "Quantity should be a valid number"
        # if len(description) < 4:
        #     error_message["description"]  = "Description should contain a minimum of four characters"
        # if  error_message:
            return render(request, "psyadmin/edit-products.html",{ 'content': content,'categoryobjs': categoryobjs,'brands': brands,'error_message':error_message} )

        else:
            content.name = name

            # Retrieve the category if it exists, otherwise assign a default category
            categoryobject = Category.objects.get(name=category_name)
            content.category = categoryobject

            brand_id = request.POST.get("brand")
            content.brand = Brand.objects.get(id=brand_id) if brand_id else None

            # # Check if new images are provided
            # if 'image' in request.FILES:
            #     # Delete the existing images
            #     for image in images:
            #         os.remove(image.image.path)
            #         image.delete()

            #     # Save new images
            #     for image_file in request.FILES.getlist('image'):
            #         ProductImage.objects.create(product=content, image=image_file)

            if 'image' in request.FILES:
                # Save new images
                for image_file in request.FILES.getlist('image'):
                    ProductImage.objects.create(product=content, image=image_file)

                # for image_id in selected_images:
                #     image = ProductImage.objects.get(id=image_id)
                #     image.delete()
                    

            content.save()
            return redirect('products')

    context = {
        'content': content,
        'categoryobjs': categoryobjs,
        'brands': brands,
        'images':images
      
    }

    return render(request, "psyadmin/edit-products.html", context)


def deleteproducts(request, someid):
    content = get_object_or_404(Products, id=someid)

    # Delete the product
    content.delete()

    # Redirect to a specific URL or view
    return redirect('products') 

def deletevariants(request, someid):
    variant = get_object_or_404(Productvariant, id=someid)
    # variant = Productvariant.objects.get(id=item_id)
    product=variant.product
    productid=product.id

    # Delete the product
    variant.delete()

    # Redirect to a specific URL or view
    # return redirect('productvariant')
    return redirect(productvariant,productid)

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
        elif not name.replace(" ", "").isalpha():
            error = "Category name can't contain numbers or special characters"
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
       

        if len(name)==0:
            error="Category name field can't be empty"
        elif not name.replace(" ", "").isalpha():
            error = "Category name can't contain numbers or special characters"

        elif len(name)<3:
            error="Category name should atleast have 4 letters"
        # elif Category.objects.filter(name=name):
        #     error="Same Category name is not allowed"
        elif len(name)>20:
            error="Category name atmost can have only 20 letters"
        else:
            obj.name=name
            
           
            edited = Category(id=someid, name=name)
            edited.save()
           
            return redirect(categories)
        if error:
            return render(request,"psyadmin/editcategories.html",{"obj":obj,"error":error,"categoryobjs":categoryobjs})

    return render(request,"psyadmin/editcategories.html",{"obj":obj,"categoryobjs":categoryobjs})



@never_cache
def users(request):
    if "adminuser" in request.session:
        datas=customer.objects.all()
        if request.method == "POST":
            entered_user = request.POST.get("searchitem")
            datas = customer.objects.filter(name__icontains=entered_user)
            return render(request, "psyadmin/users.html", {"datas": datas})
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

# from django.contrib import messages

def orders(request):
    if "adminuser" in request.session:
        orderobj = Order.objects.all()
        itemobj = OrderItem.objects.all()


        

        return render(request,"psyadmin/orders.html",{"orderobj":orderobj,"itemobj":itemobj})
    else:
        return redirect(admin_login)
    
def orderitems(request,item_id):
    orderobj = Order.objects.all()
    orderitemobj = OrderItem.objects.filter(order__id=item_id)

    context = {
        'orderobj':orderobj, 
        'orderitemobj':orderitemobj
    }

    return render(request, "psyadmin/orderitems.html",context)

from django.shortcuts import get_object_or_404

def update_orderstatus(request, item_id):
    order = get_object_or_404(Order, id=item_id)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        order.order_status = new_status
        order.save()
        
        return redirect(orders)
        
    context = {
        'order': order,
        'order_status_choices': Order.ORDER_STATUS_CHOICES
    }

    return render(request, "psyadmin/update_orderstatus.html", context)



def coupon_management(request):
    if 'adminuser' in request.session:
        datas = Coupon.objects.all()
        return render(request, "psyadmin/coupon-management.html", {"datas": datas})
    else:
        # Handle the case where the user is not authenticated as an admin
        return redirect('admin_login')  # Replace 'login' with the appropriate URL name

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


def productoffer(request):
    offerobj = ProductOffer.objects.all()

    context={
        'offerobj':offerobj,
    }
    return render(request,"psyadmin/productoffers.html",context)

def productoffer_is_expired(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = ProductOffer.objects.get(id=someid)
        obj.is_expired = True
        obj.save()
    except ProductOffer.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('productoffer')  # Replace 'coupon_management' with the appropriate URL name

def productoffer_available(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = ProductOffer.objects.get(id=someid)
        obj.is_expired = False
        obj.save()
    except ProductOffer.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('productoffer')  # Replace 'coupon_management' with the appropriate URL name


def addnew_productoffer(request):
    pobj = Products.objects.all()
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    if request.method == "POST":
        user = request.session["username"]
        offercode = request.POST.get("offercode")
        discount = request.POST.get("discount")
        product_name = request.POST.get("product")
        product = Products.objects.get(name=product_name)

        error_message = {}

        if not offercode:
            error_message["offercode"] = "Coupon code field can't be empty"

        if not discount:
            error_message["discount"] = "Discount price field can't be empty"

        if not product:
            error_message["category"] = "Minimum amount field can't be empty"

        if ProductOffer.objects.filter(offercode=offercode).exists():
            error_message["offercode"] = "Coupon code already exists"

        if error_message:
            datas = ProductOffer.objects.all()
            return render(request, "psyadmin/add_categoryoffer.html", {"datas": datas, "error_message": error_message})
            

        cus = customer.objects.get(username=user)

        catobj = ProductOffer(offercode=offercode, discount=discount, product=product, customer=cus)
        catobj.save()

        return redirect('productoffer')  

    datas = ProductOffer.objects.all()
    error_message = {}
    return render(request, "psyadmin/add_productoffer.html", {"datas": datas, "error_message": error_message,"pobj":pobj})



def categoryoffer(request):
    offerobj = CategoryOffer.objects.all()

    context={
        'offerobj':offerobj,
    }
    return render(request,"psyadmin/categoryoffers.html",context)

def categoryoffer_is_expired(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = CategoryOffer.objects.get(id=someid)
        obj.is_expired = True
        obj.save()
    except CategoryOffer.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('categoryoffer')  # Replace 'coupon_management' with the appropriate URL name

def categoryoffer_available(request, someid):
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    try:
        obj = CategoryOffer.objects.get(id=someid)
        obj.is_expired = False
        obj.save()
    except CategoryOffer.DoesNotExist:
        # Handle the case where the coupon with the given ID does not exist
        pass

    return redirect('categoryoffer')  # Replace 'coupon_management' with the appropriate URL name


def addnew_categoryoffer(request):
    catobj = Category.objects.all()
    if 'adminuser' not in request.session:
        return redirect('login')  # Replace 'login' with the appropriate URL name

    if request.method == "POST":
        user = request.session["username"]
        offercode = request.POST.get("offercode")
        discount = request.POST.get("discount")
        category_id = request.POST.get("category")

        error_message = {}

        if not offercode:
            error_message["offercode"] = "Coupon code field can't be empty"

        if not discount:
            error_message["discount"] = "Discount price field can't be empty"

        if not category_id:
            error_message["category"] = "Minimum amount field can't be empty"

        if CategoryOffer.objects.filter(offercode=offercode).exists():
            error_message["offercode"] = "Coupon code already exists"

        if error_message:
            datas = CategoryOffer.objects.all()
            return render(request, "psyadmin/add_categoryoffer.html", {"datas": datas, "error_message": error_message})

        category = Category.objects.get(pk=category_id)
        cus = customer.objects.get(username=user)

        catobj = CategoryOffer(offercode=offercode, discount=discount, category=category,customer=cus)
        catobj.save()

        return redirect('categoryoffer')  

    datas = CategoryOffer.objects.all()
    error_message = {}
    return render(request, "psyadmin/add_categoryoffer.html", {"datas": datas, "error_message": error_message,"catobj":catobj})

# from django.http import FileResponse
# import io
# from reportlab.pdfgen import canvas
# from reportlab.lib.units import inch
# from reportlab.platypus import Table, TableStyle
# from reportlab.lib.pagesizes import letter
# from datetime import datetime
# from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
# from reportlab.lib.pagesizes import letter
# from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
# from reportlab.lib.styles import getSampleStyleSheet
# from reportlab.lib import colors
# import xlsxwriter


# def sales_report(request):
#     if request.method=="POST":
#         if "show" in request.POST:
#             start_date=request.POST.get("start_date")
#             end_date=request.POST.get("end_date")
#             orderobjs = Order.objects.filter(orderdate__range=[start_date, end_date])
#             if orderobjs.count()==0:
#                 message="Sorry! No orders in this particular date range"
#                 context={"orderobjs":orderobjs,"message":message}
#             else:

#                 context={"orderobjs":orderobjs}
#             return render(request,"storeadmin/salesreport.html",context)
#         elif "download" in request.POST:
#             start_date_str = request.POST.get('start_date')
#             end_date_str = request.POST.get('end_date')

#             start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
#             end_date = datetime.strptime(end_date_str, "%Y-%m-%d")

#             buf = io.BytesIO()
#             doc = SimpleDocTemplate(buf, pagesize=letter)
#             elements = []

#             # Add heading
#             styles = getSampleStyleSheet()
#             heading_style = styles['Heading1']
#             heading = "Sales Report"
#             heading_paragraph = Paragraph(heading, heading_style)
#             elements.append(heading_paragraph)
#             elements.append(Spacer(1, 12))  # Add space after heading

#             ords = Orders.objects.filter(orderdate__range=[start_date, end_date])
            

#             if ords:
#                 data = [['Sl.No.', 'Name', 'Product', 'House', 'Order Date', 'Order Status', 'Quantity']]
#                 slno = 0
#                 for ord in ords:
#                     slno += 1
#                     row = [slno, ord.user.name, ord.product.name, ord.address.house, ord.orderdate, ord.orderstatus, ord.quantity]
#                     data.append(row)

#                 table = Table(data)
#                 table.setStyle(TableStyle([
#                     ('BACKGROUND', (0, 0), (-1, 0), colors.gray),
#                     ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
#                     ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
#                     ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
#                     ('FONTSIZE', (0, 0), (-1, 0), 12),
#                     ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
#                     ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
#                     ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
#                     ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
#                     ('FONTSIZE', (0, 1), (-1, -1), 10),
#                     ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
#                 ]))

#                 elements.append(table)
#             else:
#                 elements.append(Paragraph("No orders", styles['Normal']))
#             if elements:

#                 doc.build(elements)
#                 buf.seek(0)
#                 return FileResponse(buf, as_attachment=True, filename='Orders.pdf')
        
#         elif "downloadinexcel" in request.POST:

#             start_date_str = request.POST.get('start_date')
#             end_date_str = request.POST.get('end_date')

#             start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
#             end_date = datetime.strptime(end_date_str, "%Y-%m-%d")



#             ords = Orders.objects.filter(orderdate__range=[start_date, end_date])

#             # Create Excel workbook and worksheet
#             workbook = xlsxwriter.Workbook("Sales_Report.xlsx")
#             worksheet = workbook.add_worksheet('Sales Report')

#             # Write the table headers
#             headers = ['Sl.No.', 'Name', 'Product', 'House', 'Order Date', 'Order Status', 'Quantity']
#             for col, header in enumerate(headers):
#                 worksheet.write(0, col, header)

#             # Write the data rows
#             row = 1
#             for slno, ord in enumerate(ords, start=1):
#                 worksheet.write(row, 0, slno)
#                 worksheet.write(row, 1, ord.user.name)
#                 worksheet.write(row, 2, ord.product.name)
#                 worksheet.write(row, 3, ord.address.house)
#                 worksheet.write(row, 4, str(ord.orderdate))
#                 worksheet.write(row, 5, ord.orderstatus)
#                 worksheet.write(row, 6, ord.quantity)
#                 row += 1

#             workbook.close()

#             # Create a file-like buffer to receive the workbook data
#             buf = io.BytesIO()
            
#             buf.seek(0)
            

#             # Return the Excel file as a FileResponse
#             return FileResponse(buf, as_attachment=True, filename='Sales_Report.xlsx', content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')


#     return render(request,"storeadmin/sales-report.html")


def sales_report(request):
    if 'adminuser' in request.session:
        if request.method == 'POST':
            if "show" in request.POST:
                start_date = request.POST.get("start_date")
                end_date = request.POST.get("end_date")
                orderobjs = Order.objects.filter(date_ordered__range=[start_date, end_date])[:1]
                itemobj = OrderItem.objects.filter(order=orderobjs).first()
                if orderobjs.count() == 0:
                    message = "Sorry! No orders in this particular date range"
                    context = {"orderobjs": orderobjs, "itemobj": itemobj, "message": message}
                else:
                    context = {"orderobjs": orderobjs,"itemobj":itemobj}
                return render(request, "psyadmin/sales-report.html", context)
            
            elif "download" in request.POST:
                start_date_str = request.POST.get('start_date')
                end_date_str = request.POST.get('end_date')
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                orders = Order.objects.filter(date_ordered__range=[start_date, end_date])
                orderitem = OrderItem.objects.filter(order=orders).first()
                if orders:
                    response = HttpResponse(content_type='application/pdf')
                    response['Content-Disposition'] = 'attachment; filename="Sales_Report.pdf"'
                    p = canvas.Canvas(response, pagesize=letter)
                    p.setFont("Helvetica-Bold", 14)
                    p.drawCentredString(300, 750, "Sales Report")
                    p.setFont("Helvetica-Bold", 12)
                    p.drawString(50, 700, "Sl.No.")
                    p.drawString(100, 700, "Name")
                    p.drawString(200, 700, "Product")
                    p.drawString(300, 700, "House")
                    p.drawString(400, 700, "Order Date")
                    p.drawString(500, 700, "Order Status")
                    p.drawString(600, 700, "Quantity")
                    p.setFont("Helvetica", 12)
                    y = 680
                    slno = 0
                    for order in orders:
                        slno += 1
                        p.drawString(50, y, str(slno))
                        p.drawString(100, y, order.customer.name)
                        p.drawString(200, y, orderitem.variant.product.name)
                        p.drawString(300, y, order.address)
                        p.drawString(400, y, str(order.date_ordered))
                        p.drawString(500, y, order.order_status)
                        p.drawString(600, y, str(order.get_cart_items))
                        y -= 20
                    p.showPage()
                    p.save()
                    return response
                else:
                    messages.error(request, "No orders found in the specified date range.")
                    return redirect('sales_report')
                
            elif "downloadinexcel" in request.POST:
                start_date_str = request.POST.get('start_date')
                end_date_str = request.POST.get('end_date')
                start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
                end_date = datetime.strptime(end_date_str, "%Y-%m-%d")
                orders = Order.objects.filter(date_ordered__range=[start_date, end_date])
                orderitems = OrderItem.objects.filter(order=orders).first()
                if orders:
                    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
                    response['Content-Disposition'] = 'attachment; filename="Sales_Report.xlsx"'
                    workbook = xlsxwriter.Workbook(response, {'in_memory': True})
                    worksheet = workbook.add_worksheet('Sales Report')
                    bold = workbook.add_format({'bold': True})
                    headers = ['Sl.No.', 'Name', 'Product', 'House', 'Order Date', 'Order Status', 'Quantity']
                    for col, header in enumerate(headers):
                        worksheet.write(0, col, header, bold)
                    row = 1
                    slno = 0
                    for order in orders:
                        slno += 1
                        worksheet.write(row, 0, slno)
                        worksheet.write(row, 1, order.customer.name)
                        worksheet.write(row, 2, orderitems.variant.product.name)
                        worksheet.write(row, 3, order.address)
                        worksheet.write(row, 4, str(order.date_ordered))
                        worksheet.write(row, 5, order.order_status)
                        worksheet.write(row, 6, order.get_cart_items)
                        row += 1
                    workbook.close()
                    return response
                else:
                    messages.error(request, "No orders found in the specified date range.")
                    return redirect('sales_report')
        return render(request, "psyadmin/sales-report.html")
    else:
        return redirect('admin_login')