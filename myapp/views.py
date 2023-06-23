from datetime import date,timezone
from datetime import datetime
from django.core.exceptions import ObjectDoesNotExist
import re
from django.shortcuts import get_object_or_404, render,redirect
from django.db.models import Q
import razorpay
from psykicks.settings import RAZORPAY_API_SECRET_KEY,RAZORPAY_API_KEY
from django.contrib import messages
from decimal import Decimal
from django.views import View
import requests
import random
from . models import *
from .forms import *
from django.http import HttpResponse, JsonResponse
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage



# Create your views here.
def index(request):
    
    datas = Products.objects.all()
    category = Category.objects.all()
    brand = Brand.objects.all()
    product_offerobj = ProductOffer.objects.all()
    category_offerobj = CategoryOffer.objects.all()
    
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')

    atoz_id = request.GET.get('ATOZ')
    ztoa_id = request.GET.get('ZTOA')
    new_productid = request.GET.get('NEWPRODUCT')
    old_productid = request.GET.get('OLDPRODUCT')

    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)
    if atoz_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('lower_name')
    if ztoa_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('-lower_name')
    if new_productid:
        datas = datas.filter(condition="New")
    if old_productid:
        datas = datas.filter(condition="Old")
    

    if request.method == "POST":
        entered_product = request.POST.get("searchitem")
        datas = Products.objects.filter(name__icontains=entered_product)
        return render(request, "myapp/index.html", {"datas": datas})
    
    context={
        'datas':datas,
        'category': category,
        'brand': brand,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
        'category_offerobj':category_offerobj,
        'product_offerobj':product_offerobj,
    }
    return render(request,"myapp/index.html",context)
     
def userindex(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)

        orders = Order.objects.filter(customer=user)
        if orders.exists():
            order = orders.first()
        else:
            order = Order.objects.create(customer=user)

        items = order.orderitem_set.all()
        cartItems = order.get_cart_items
    else:
        items = []
        order = {'get_cart_total': 0, 'get_cart_items': 0, 'shipping': False}
        cartItems = order['get_cart_items']

    datas = Products.objects.all()
    colors = Color.objects.all()
    category = Category.objects.all()
    brand = Brand.objects.all()
    size = Size.objects.all()
    product_offerobj = ProductOffer.objects.all()
    category_offerobj = CategoryOffer.objects.all()
    
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')

    atoz_id = request.GET.get('ATOZ')
    ztoa_id = request.GET.get('ZTOA')
    new_productid = request.GET.get('NEWPRODUCT')
    old_productid = request.GET.get('OLDPRODUCT')

    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)
    if selected_color:
        datas = datas.filter(color__name=selected_color)
    if selected_size:
        datas = datas.filter(size__name=selected_size)
    if atoz_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('lower_name')
    if ztoa_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('-lower_name')
    if new_productid:
        datas = datas.filter(condition="New")
    if old_productid:
        datas = datas.filter(condition="Old")



    username = request.session["username"]
    user = customer.objects.filter(username=username).first()
    wishlist_items = Wishlist.objects.filter(customer=user)
    count = wishlist_items.count()

    cart_count = Cart.objects.filter(user=user).count()

    # for product in datas:
    #     product_variants = Productvariant.objects.filter(product=product)
    #     variants[product.id] = product_variants
    # print("varianttssss>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",variants)

    context = {
        'datas': datas,
        # 'variants':variants,
        'cartItems': cartItems,
        'colors': colors,
        'category': category,
        'brand': brand,
        'size': size,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
        'selected_color':selected_color,
        'category_offerobj':category_offerobj,
        'product_offerobj':product_offerobj,
        'count':count,
        'cart_count':cart_count
    }

    if request.method == "POST":
        entered_product = request.POST.get("searchitem")
        datas = Products.objects.filter(name__icontains=entered_product)
        return render(request, "myapp/userindex.html", {"datas": datas})

    return render(request, "myapp/userindex.html", context)




def signout(request):
    if 'username' in request.session:
        # del request.session['username']
        request.session.flush()
    return redirect('index')



def login(request):

    error_message = {}
    alert_message = request.GET.get('alert')
    context = {'alert_message': alert_message}
    
    
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']

        user = customer.objects.filter(username=username).first()
        if user is not None and user.isblocked:
            error_message["alert"] = "Your account is blocked. Please contact the administrator."
            return render(request, "myapp/login.html", {'error_message': error_message})


    
        my_user = customer.objects.filter(username=username , password=password).count()
        print(my_user,"^^^^^^^^^^^^^^^^^^^^^^")

        if my_user ==1 :
            request.session['username'] = username
            return redirect('userindex')
           
        else:
            if not customer.objects.filter(username=username).exists():
                error_message["username"] = "Enter valid username!!"
            else:
                error_message["password"] = "Incorrect password!!"
            

            return render(request,"myapp/login.html",{'error_message': error_message,"username":username,"password":password})

            
    return render(request,"myapp/login.html",context)


def signup(request):
    if request.method == "POST":
        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        phonenumber = request.POST['phonenumber']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        error_message = {}

        if customer.objects.filter(username=username):
            error_message["username"] = "Username already exists. Please try a different username."

        if len(username) > 10:
            error_message["username"] = "Username must be under 10 characters." 

        if not all(c.isalnum() or c.isspace() for c in name):
            error_message["name"] = "Invalid string entry" 

        if customer.objects.filter(email=email):
            error_message["email"] = "Email already registered. Please try a different email."

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error_message["email"]="Invalid Email"

        if int(phonenumber)<0:
            error_message["phonenumber"] = "phone number should be positive numbers"
        
        if phonenumber=="0":
            error_message["phonenumber"] = "invalid phone number"

        if phonenumber[0]=="0":
            error_message["phonenumber"] = "Invalid format for phone number"

        if phonenumber.isalpha():
            error_message["phonenumber"] = "Phone number cannot be alphabetic"
        
        if password != confirm_password:
            error_message["password"] = "Passwords do not match."

        if len(password) < 3:
            error_message["password"] = "Your password is too weak"

        if error_message:
            return render(request, "myapp/signup.html", {'error_message': error_message, "username": username, "name": name, "email": email, "phonenumber": phonenumber, "password": password, "confirm_password": confirm_password})

       
        myuser = customer(username=username, name=name, email=email, phonenumber=phonenumber, password=password, isblocked=False, is_verified=False)
        myuser.save()


        return redirect('login')

    return render(request, "myapp/signup.html")


def generate_otp():
    return str(random.randint(1000, 9999))


def send_otp(phonenumber, otp):
    url = 'https://www.fast2sms.com/dev/bulkV2'
    payload = f'sender_id=TXTIND&message={otp}&route=v3&language=english&numbers={phonenumber}'
    headers = {
        'authorization': "mEgP0Z5wnldKSerOu1GW8qUbVctH3jkYaM7QCI4Jzp69XNT2ALFmiofRb467D0rSOWVB3qp8J5HYeIvt",
        'Content-Type': "application/x-www-form-urlencoded"
    }
    response = requests.request("POST", url, data=payload, headers=headers)
    print(response.text)

def otp_login(request):
    
    if request.method == 'POST':
        phonenumber = request.POST.get('phonenumber')

        try:
            user = customer.objects.get(phonenumber=phonenumber)
        except ObjectDoesNotExist:
            error_message = "User not found. Please register or enter a valid phone number."
            return render(request, 'myapp/otp_login.html', {"error_message": error_message})

        if user.isblocked:
            error_message = "Your account has been blocked"
            return render(request, 'myapp/otp_login.html', {"error_message": error_message})
        
        phonenumber = request.POST.get('phonenumber')
        otp = generate_otp()
        
        request.session['U_otp'] = otp
        request.session['U_phone'] = phonenumber
        
        send_otp(phonenumber, otp)
        
        return redirect('otp_verify')
    return render(request, 'myapp/otp_login.html')



def otp_verify(request):
    
    if 'U_otp' in request.session and 'U_phone' in request.session:
        exact_otp = request.session['U_otp']
        phonenumber = request.session['U_phone']
        if request.method == 'POST':
           
            user_otp = request.POST.get('otp')
            if exact_otp == user_otp:
                try:
                    
                    user = customer.objects.get(phonenumber=phonenumber)
                    
                    if user is not None:

                        request.session['username'] = user.username 
                        request.session['phonenumber'] = phonenumber
                        messages.success(request, "Login completed successfully")
                        return redirect('userproduct')
                except customer.DoesNotExist:
                    messages.error(request, "This User doesn't Exist")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        return render(request, 'myapp/verify_otp.html', {'phonenumber': phonenumber})
    else:
        return redirect('otp_login')
    
def userproduct(request):
    if "username" in request.session:
        datas=Products.objects.all()
        category = Category.objects.all()
        colors = Color.objects.all()
        brand = Brand.objects.all()
        size = Size.objects.all()
        variant=Productvariant.objects.all()
        
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')

    atoz_id = request.GET.get('ATOZ')
    ztoa_id = request.GET.get('ZTOA')
    new_productid = request.GET.get('NEWPRODUCT')
    old_productid = request.GET.get('OLDPRODUCT') 

    username = request.session["username"]
    user = customer.objects.get(username=username)
    wishlist_items = Wishlist.objects.filter(customer=user)
    count = wishlist_items.count()

    cart_count = Cart.objects.filter(user=user).count()

    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)

    if atoz_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('lower_name')
    if ztoa_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('-lower_name')
    if new_productid:
        datas = datas.filter(condition="New")
    if old_productid:
        datas = datas.filter(condition="Old")
   


    page = request.GET.get('page',1)
    paginator = Paginator(datas,12)
    try:
        datas = paginator.page(page)
    except PageNotAnInteger: 
        datas = paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)

    


    context = {
        'datas': datas,
        "variant":variant,
        'category':category,
        'colors':colors,
        'brand':brand,
        'size':size,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
       'count':count,
        'cart_count':cart_count,
     
    }

    if request.method == "POST":
        entered_product = request.POST.get("searchitem")
        datas = Products.objects.filter(name__icontains=entered_product)
        return render(request, "myapp/userproduct.html", {"datas": datas})

    return render(request,"myapp/userproduct.html",context)
    # else:
        # return redirect(userindex)
    
def product(request):
  
    datas=Products.objects.all()
    category = Category.objects.all()
    colors = Color.objects.all()
    brand = Brand.objects.all()
    size = Size.objects.all()
    variant=Productvariant.objects.all()
        
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')

    atoz_id = request.GET.get('ATOZ')
    ztoa_id = request.GET.get('ZTOA')
    new_productid = request.GET.get('NEWPRODUCT')
    old_productid = request.GET.get('OLDPRODUCT') 

    if request.method == "POST":
        entered_product = request.POST.get("searchitem")
        datas = Products.objects.filter(name__icontains=entered_product)
        return render(request, "myapp/product.html", {"datas": datas})
    
    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)

    if atoz_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('lower_name')
    if ztoa_id:
        datas = datas.extra(select={'lower_name': "LOWER(name)"}).order_by('-lower_name')
    if new_productid:
        datas = datas.filter(condition="New")
    if old_productid:
        datas = datas.filter(condition="Old")

    page = request.GET.get('page',1)
    paginator = Paginator(datas,12)
    try:
        datas = paginator.page(page)
    except PageNotAnInteger: 
        datas = paginator.page(1)
    except EmptyPage:
        datas = paginator.page(paginator.num_pages)

    context = {
        'datas': datas,
        "variant":variant,
        'category':category,
        'colors':colors,
        'brand':brand,
        'size':size,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
    }
    
    return render(request,"myapp/product.html",context)
        

def blog(request):

    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()
        cart_count = Cart.objects.filter(user=user).count()
        context={
            'count':count,
            'cart_count':cart_count
        }
    return render(request,"myapp/blog.html",context)

def contact(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()
        cart_count = Cart.objects.filter(user=user).count()
        context={
            'count':count,
            'cart_count':cart_count
        }
    return render(request,"myapp/contact.html",context)

def about(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()
        cart_count = Cart.objects.filter(user=user).count()
        context={
            'count':count,
            'cart_count':cart_count
        }
    return render(request,"myapp/about.html",context)


def pdetails(request, product_id):
    if request.method=="POST":
        # quantity=request.POST.get("quantity")
        # pdtobj=Products.objects.get(id=product_id)
        # # print(quantity,"HHHHHHHHHHHHHHH")
        # username=request.session.get("username")
        # user=customer.objects.get(username=username)
        # total=Decimal(quantity)*pdtobj.price
        
        # if pdtobj in Cart.user:
        #     quantity += quantity
        #     cartobj=Cart.user(quantity=quantity,total=total)
        #     cartobj.save()
        # else:
        #     cartobj=Cart(user=user,product=pdtobj,quantity=quantity,total=total)
        #     cartobj.save()
        alert_message = "Please Login to add products to your cart."
        return redirect(f"/login/?alert={alert_message}")

    product = Products.objects.prefetch_related('images').filter(id=product_id).first()
    pdtobj=Products.objects.get(id=product_id)
    variant=Productvariant.objects.filter(product=pdtobj)
    pdtobj1 = variant.first()
    # print(">>>>>>>>>>>>>>>?????????????????>>>>>>>>>>>>>>>>>>?????????????????>>>>>>>>>>>??????????>>>>>>>>",pdtobj1)
    images = product.images.all() if product else []
    products_in_same_category = Products.objects.filter(category=product.category)
    
    return render(request, 'myapp/product-detail.html', {
        'pdtobj1':pdtobj1,
        'product': product,
        'images': images,
        'products_in_same_category': products_in_same_category
    })

def user_pdetails(request, product_id):
    sizes = Size.objects.all()
    colors = Color.objects.all()
    

    pdt=Products.objects.get(id=product_id)


    product = get_object_or_404(Products, id=product_id)
    user=customer.objects.get(username=request.session["username"])
    pdtvariant = Productvariant.objects.filter(product=product)
    pdtobj1 = pdtvariant.first()
    images = product.images.all() 
    products_in_same_category = Products.objects.filter(category=product.category)
    username = request.session["username"]
    user = customer.objects.get(username=username)
    wishlist_items = Wishlist.objects.filter(customer=user)
    count = wishlist_items.count()
    cart_count = Cart.objects.filter(user=user).count()
    error_message = {}
    unique_colors = set()
    unique_sizes = set()

    for variant in pdtvariant:
        colorobj = variant.color.all()
        sizeobj = variant.size.all()
        
        # Add each color name to the set
        for color in colorobj:
            unique_colors.add(color.name)

        for size in sizeobj:
            unique_sizes.add(size.name)

    # Print the unique color names
    for color_name in unique_colors:
        print(color_name)

    distinct_colors = ", ".join(unique_colors)
    distinct_sizes = ", ".join(unique_sizes)

    if request.method == "POST":

        # if "updatevariant" in request.POST:
        #     size=request.POST["size"]
        #     color=request.POST["color"]
        #     product=Products.objects.get(id=product_id)

        #     product = Products.objects.prefetch_related('images').filter(id=product_id).first()
        #     pdtvariant=Productvariant.objects.filter(product=product)
        #     pdtobj1=Productvariant.objects.get(id=1)
        #     print("#################",pdtobj1.product.name)


        #     images = product.images.all() 
        #     products_in_same_category = Products.objects.filter(category=product.category)

        #     username = request.session["username"]
        #     user = customer.objects.get(username=username)
        #     wishlist_items = Wishlist.objects.filter(customer=user)
        #     count = wishlist_items.count()

        #     try:
        #         pdtobj1 = Productvariant.objects.filter(product=product, size=size, color=color).first()
        #         images = product.images.all()
        #         products_in_same_category = Products.objects.filter(category=product.category)

        #         username = request.session["username"]
        #         user = customer.objects.get(username=username)
        #         wishlist_items = Wishlist.objects.filter(customer=user)
        #         count = wishlist_items.count()

        #         return render(request, 'myapp/user-pdetails.html', {
        #             'pdtobj1': pdtobj1,
        #             'images': images,
        #             'products_in_same_category': products_in_same_category,
        #             'count': count,
        #             'sizes': sizes,
        #             'colors': colors,
        #             'distinct_colors':distinct_colors,
        #             "distinct_sizes":distinct_sizes
       
                    
        #         })
        #     except Productvariant.DoesNotExist:
        #         error_message["name"]="Out of stock"
        #         return render(request, 'myapp/user-pdetails.html', {
        #             "error_message":error_message,
        #                     'pdtobj1': pdtobj1,
        #                      'images': images,
        #                      'products_in_same_category': products_in_same_category,
        #                      'count':count,
        #                      'cart_count':cart_count,
        #                     'sizes':sizes,
        #                     'colors':colors,
        #                     'distinct_colors':distinct_colors,
        #                     "distinct_sizes":distinct_sizes
       
                           
        #                 })

        if "addtocart" in request.POST:

            quantity = request.POST.get("quantity")
            quantity=int(quantity)
            pdtobj = Products.objects.get(id=product_id)
            size=request.POST["size"]
            color=request.POST["color"]
            print("#############",size,color)
            if size=="Choose an option" and color =="Choose an option":
                error="Please select valid credentials before adding a product to the Cart"
                return render(request, 'myapp/user-pdetails.html', {
                "error":error,
                'pdt':pdt,
                'pdtobj1': pdtobj1,
                'images': images,
                'products_in_same_category': products_in_same_category,
                'count':count,
                'cart_count':cart_count,
                'sizes':sizes,
                'colors':colors,
                'distinct_colors':distinct_colors,
                "distinct_sizes":distinct_sizes
       
            
            }) 
            try:  
                pdtvariant=Productvariant.objects.get(product=pdtobj,size=size,color=color)
            except:
                error="Out of stock"
                return render(request, 'myapp/user-pdetails.html', {
                "error":error,
                'pdt':pdt,
                'pdtobj1': pdtobj1,
                'images': images,
                'products_in_same_category': products_in_same_category,
                'count':count,
                'cart_count':cart_count,
                'sizes':sizes,
                'colors':colors,
                'distinct_colors':distinct_colors,
                "distinct_sizes":distinct_sizes
       
            
            })
                    
            username = request.session.get("username")
            user = customer.objects.get(username=username)

            
            total = Decimal(quantity) * pdtvariant.price 
            
            
            try:
                # Check if the product is already in the cart
                cartobj = Cart.objects.get(user=user, variant=pdtvariant,product=pdtobj)
                cartobj.quantity += quantity  # Increase the quantity
                cartobj.total += total  # Update the total
                cartobj.save()
                return redirect(usercart)
            except Cart.DoesNotExist:
                cartobj = Cart(user=user,product=pdtobj, variant=pdtvariant, quantity=quantity, total=total)
                cartobj.save()
                return redirect(usercart)
            
                
    return render(request, 'myapp/user-pdetails.html', {
        'pdt':pdt,
        'pdtobj1': pdtobj1,
        'images': images,
        'products_in_same_category': products_in_same_category,
        'count':count,
        'cart_count':cart_count,
        'sizes':sizes,
        'colors':colors,
      'distinct_colors':distinct_colors,
      "distinct_sizes":distinct_sizes
       
    })



def addtocart(request, product_id):
    if request.method == "POST":
        if "username" in request.session:
            
            username = request.session["username"]
            user = customer.objects.get(username=username)
        
            product = Products.objects.get(id=product_id)
            # quantity = request.POST.get("quantity")
            variant = Productvariant.objects.filter(product=product).first()


            cartobjs=Cart.objects.filter(user=user)
            # for item in cartobjs:
            #     if item.product==product:
            #         item.quantity+=int(quantity)
            #         item.save()
            #         return redirect('usercart') 

            
            for item in cartobjs:
                if item.product==product:
                    return redirect ('userproduct')
            cartobj = Cart(user=user, product=product,total=variant.price*variant.stock, quantity=1)
            cartobj.save()
            return redirect('usercart') 
        else:
            return redirect('login') 

    return redirect('userproduct')

def updatevariant(request):
    colorid=request.GET["colorId"]
    sizeid=request.GET["sizeId"]
    productid=request.GET["productId"]
    color=Color.objects.get(id=colorid)
    size=Size.objects.get(id=sizeid)
    print("###########",size.name,color.name,productid)




    product=Products.objects.get(id=productid)
    try:
        variant=Productvariant.objects.get(product=product,size=size,color=color)
    except: 
        varianterror="Out Of Stock"
        return JsonResponse({"varianterror":varianterror})

    variantprice=variant.price


    return JsonResponse({"variantprice":variantprice})

  


    # if request.method=="POST":
    #     size=request.POST["size"]
    #     color=request.POST["color"]
    #     product=Products.objects.get(id=item_id)
    #     variant=Productvariant.objects.get(product=product,size=size,color=color)

    # return redirect(usercart)

def list_addtocart(request,product_id):
    username = request.session["username"]
    user = customer.objects.get(username=username)
    wishobj=Wishlist.objects.get(id=product_id)
    product=wishobj.product
    variant=wishobj.variant
    cartobjcount=Cart.objects.filter(user=user,product=product,variant=variant).count()
    if cartobjcount!=0:
        return redirect(wishlist)
    else:
        cartobj=Cart(user=user,variant=variant, product=product,total=variant.price*1, quantity=1)
        cartobj.save()
        return redirect(usercart)
        


def cart(request):
        cartobj = Cart.objects.all()

        datas = {
            'cartobj' : cartobj
        }

        return render(request, "myapp/cart.html", datas)
    


def usercart(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        cartobj = Cart.objects.filter(user=user)
        print(cartobj,"7822222222222222222222222222222222222222222222222222222222222222222222222222222222222222")
        

        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()
        cart_count = Cart.objects.filter(user=user).count()
       
        quantsum=0
        total_price=0

        for item in cartobj:
            variant = item.variant
            colors = variant.color.all()
            sizes = variant.size.all()
            item.variant = variant
            item.colors = colors
            item.sizes = sizes

            quantsum+=item.quantity
            total_price += item.total

        datas = {
            'cartobj': cartobj,
             "total_price":total_price,
            "quantsum":quantsum,
            'count':count,
            'cart_count':cart_count,
            # 'item.colors':item.colors,
            # 'item.sizes':item.sizes
        }
        return render(request, "myapp/usercart.html", datas)
    else:
        return render(request, "myapp/userindex.html")



def quantity_inc(request, item_id):
    obj = Cart.objects.get(id=item_id)
    product = obj.product
    variant = obj.variant
    user = obj.user

   
    existing_cart_item = Cart.objects.filter(user=user, product=product, variant=variant).first()

    if existing_cart_item:
        # Product already exists in the cart, update its quantity and total
        existing_cart_item.quantity += 1
        existing_cart_item.total += variant.price
        existing_cart_item.save()
    else:
        # Product does not exist in the cart, create a new entry
        quantity = obj.quantity + 1
        total = obj.total + variant.price
        new_cart_item = Cart(user=user, product=product, variant=variant, quantity=quantity, total=total)
        new_cart_item.save()

    
    return redirect(usercart)

    

def quantity_dec(request,item_id):
    obj = Cart.objects.get(id=item_id)
    product = obj.product
    variant = obj.variant
    user = obj.user

    existing_cart_item = Cart.objects.filter(user=user, product=product, variant=variant).first()

    if existing_cart_item:
        # Product already exists in the cart, update its quantity and total
        if existing_cart_item.quantity>1:
            existing_cart_item.quantity -= 1
            existing_cart_item.total -= variant.price
            existing_cart_item.save()
        else:
            existing_cart_item.delete()
    else:
        # Product does not exist in the cart, create a new entry
        quantity = obj.quantity - 1
        total = obj.total - variant.price
        new_cart_item = Cart(user=user, product=product, variant=variant, quantity=quantity, total=total)
        new_cart_item.save()

    return redirect(usercart)


    
def removecartitem(request,item_id):
    item = get_object_or_404(Cart, id=item_id)

    # Delete the product
    item.delete()

    # Redirect to a specific URL or view
    return redirect('usercart') 


def usercheckout(request):

    if customer.objects.get(username=request.session["username"]).isblocked:
        return redirect("login")


    if "username" in request.session:

        client = razorpay.Client(
        auth=(RAZORPAY_API_KEY, RAZORPAY_API_SECRET_KEY))
        username = request.session.get("username")
        userobj = customer.objects.get(username=username)
        addressobj = ShippingAddress.objects.filter(customer=userobj)
        cartobj = Cart.objects.filter(user=userobj)

        totalsum = 0
        for item in cartobj:
            totalsum += item.total
            
        amount=float(totalsum*100)
        currency='INR'
        data = dict(amount=amount,currency=currency,payment_capture=1)
                
        payment_order = client.order.create(data=data)
        payment_order_id=payment_order['id']
        # print(payment_order)
        


        if username is None:
            return redirect("login")
        

        user = customer.objects.get(username=username)
        cartobj = Cart.objects.filter(user=user)

        quantsum = 0
        total_price = 0
        for item in cartobj:
            variant = item.variant
            colors = variant.color.all()
            sizes = variant.size.all()
            item.variant = variant
            item.colors = colors
            item.sizes = sizes
            quantsum += item.quantity
            total_price += item.total

        coupon_discount=0
        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code=coupon).first()
        # coupon_discount = coupon_obj.discount_price

        if coupon_obj and total_price > coupon_obj.minimum_amount and not any(item.coupon for item in cartobj):

            # Check if the coupon has been applied to any other orders by the user
            # if Order.objects.filter(customer=user, cart__coupon=coupon_obj).exists():
            #     error_message = "Coupon already applied to another order."
            #     context = {
            #         "error_message": error_message,
            #         "cartobj": cartobj,
            #         "quantsum": quantsum,
            #         "total_price": total_price,
            #         "addressobj":addressobj
            #     }
            #     return render(request, "myapp/checkout.html", context)

            total_price = total_price-(coupon_obj.discount_price)

        username = request.session["username"]
        user = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()

        cart_count = Cart.objects.filter(user=user).count()

        context = {
            "cartobj": cartobj,
            "quantsum": quantsum,
            "coupon_discount":coupon_discount,
            "total_price": total_price,
            'count':count,
            'cart_count':cart_count,
            "order_id":payment_order_id,
            "api_key":RAZORPAY_API_KEY ,
            "addressobj":addressobj,
            "item.colors":item.colors,
            "item.sizes":item.sizes
        }

    if request.method == "POST":

        username = request.session.get("username")
        userobj = customer.objects.get(username=username)
        addressobj = ShippingAddress.objects.filter(customer=userobj)
        cartobj = Cart.objects.filter(user=userobj)

        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code=coupon)
        

        if "couponbutton" in request.POST:
            error_message = {}
            
            coupon = request.POST.get("coupon")
            coupon_obj = Coupon.objects.filter(coupon_code=coupon)

            if not coupon_obj.exists():
                error_message["coupon"] = "Invalid coupon"
            elif any(item.coupon for item in cartobj):
                error_message["coupon"] = "Coupon already exists"
            elif any(item.total < item.coupon.minimum_amount for item in cartobj if item.coupon):
                error_message["coupon"] = f"Amount should be greater than {coupon_obj[0].minimum_amount}"

            for item in cartobj:
                item.coupon = coupon_obj.first()
                item.save()

            success_message = "Coupon applied successfully"
            context["success_message"] = success_message
        
        if "placeorder" in request.POST:
            username = request.session.get("username")
            user = customer.objects.get(username=username)
            cartobj = Cart.objects.filter(user=user)
            addressid = request.POST.get("address")
            address = ShippingAddress.objects.get(id=addressid)
            

            date_ordered = datetime.date.today()
            print("###########",date_ordered)

            
            orderobj = Order(customer=user, date_ordered=date_ordered, total=0 ,address = address)
            orderobj.save()
            
        
            for item in cartobj:

                pdtvariant=item.variant
                product = item.product
                price = item.variant.price
                quantity=item.quantity
                itemtotal = quantity*price

                orderitemobj = OrderItem(variant=pdtvariant, order = orderobj,quantity=quantity, price=price, total=itemtotal)
                orderitemobj.save()

                pdtvariant.stock -= quantity
                pdtvariant.save()
                

                orderobj.total += item.total

                item.delete()

            orderobj.save()
            return redirect(ordercomplete)
     
        return render(request, "myapp/checkout.html", context)
      
    return render(request, "myapp/checkout.html", context)



def remove_coupon(request, coupon_id):
    carts = Cart.objects.filter(coupon__id=coupon_id)
    for cart in carts:
        cart.coupon = None
        cart.save()
    messages.success(request, 'Coupon Removed')
    return redirect('usercheckout')
  
def ordercomplete(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=user)
        count = wishlist_items.count()

        cart_count = Cart.objects.filter(user=user).count()
        
        context={
            "count":count,
            'cart_count':cart_count
        }
    return render(request,"myapp/ordercomplete.html",context) 

def orderdetails(request,item_id):
    if "username" in request.session:
        username = request.session.get('username')
        orderobj = Order.objects.filter(customer__username=username)
        orderitemobj = OrderItem.objects.filter(order__id=item_id)

        user = customer.objects.get(username=username)
        listobj = Wishlist.objects.filter(customer=user)
        count = listobj.count()
        cart_count = Cart.objects.filter(user=user).count()

        for item in orderitemobj:
            variant = item.variant
            colors = variant.color.all()
            sizes = variant.size.all()
            item.colors = colors
            item.sizes = sizes

        context = {
            'orderobj':orderobj, 
            'orderitemobj':orderitemobj,
            "count":count,
            'cart_count':cart_count,
            'item.colors':item.colors,
            'item.sizes':item.sizes
        }

    return render(request, "myapp/orderdetails.html",context)


def cancel_order(request,order_id):
    if "username" in request.session:
        username = request.session.get('username')
        userobj = customer.objects.get(username=username)

        order = Order.objects.get(id=order_id)
        order.order_status = 'cancelled'
        order.save()

        order_items = order.orderitem_set.all()
        for order_item in order_items:
            variant = order_item.variant
            quantity = order_item.quantity
            variant.stock += quantity
            variant.save()


        amount=order.total
        data = Wallet(user=userobj, amount=amount,transaction_type="cancelled_and_refund")
        data.save()

        return redirect(user_orders)

def return_order(request,order_id):
    if "username" in request.session:
        username = request.session.get('username')
        userobj = customer.objects.get(username=username)

        order = Order.objects.get(id=order_id)
        order.order_status = 'returned'
        order.save()

        order_items = order.orderitem_set.all()
        for order_item in order_items:
            variant = order_item.variant
            quantity = order_item.quantity
            variant.stock += quantity
            variant.save()

        amount=order.total
        data = Wallet(user=userobj, amount=amount,transaction_type="returned_and_refund")
        data.save()

        return redirect(user_orders)

def wallet(request):
    if "username" in request.session:
        username = request.session["username"]
        customerobj = customer.objects.get(username=username)

    
        wishlist_items = Wishlist.objects.filter(customer=customerobj)
        count = wishlist_items.count()
        user = customer.objects.get(username=username)
        cart_count = Cart.objects.filter(user=user).count()
        datas = Wallet.objects.all()

        context={
            "datas":datas,
            "count":count,
            'cart_count':cart_count
        }

        return render(request,"myapp/wallet.html",context)

def before_userprofile(request):
    return render(request,"myapp/before-userprofile.html")


def userprofile(request):
    username = request.session["username"]
    customerobj = customer.objects.get(username=username)

 
    wishlist_items = Wishlist.objects.filter(customer=customerobj)
    count = wishlist_items.count()
    user = customer.objects.get(username=username)
    cart_count = Cart.objects.filter(user=user).count()

    orderobjs = Order.objects.filter(customer=customerobj)
    
    addressobjs = ShippingAddress.objects.filter(customer=customerobj)

    context = {
        "orderobjs": orderobjs,
        "username": username,
        "addressobjs": addressobjs,
        "customerobj": customerobj,
        'count':count,
        'cart_count':cart_count
    }

    return render(request, "myapp/userprofile.html", context)

def user_orders(request):
    username = request.session["username"]
    customerobj = customer.objects.get(username=username)

 
    wishlist_items = Wishlist.objects.filter(customer=customerobj)
    count = wishlist_items.count()
    
    cart_count = Cart.objects.filter(user=customerobj).count()

    orderobjs = Order.objects.filter(customer=customerobj)

    context = {
        "orderobjs": orderobjs,
        "username": username,
        "customerobj": customerobj,
        'count':count,
        'cart_count':cart_count
    }

    return render(request, "myapp/orders.html", context)


def updateuser(request):
    if request.method=="POST":
        name=request.POST["name"]
        # name=request.POST["name"]
        email=request.POST["email"]
        phonenumber=request.POST["phonenumber"]
    
    customerobj=customer.objects.get(username=request.session.get("username"))
    customerobj.name=name
    customerobj.email=email
    customerobj.phonenumber=phonenumber
    customerobj.save()
    return redirect(userprofile)

def editaddress(request,id):
    if request.method=="POST":
        address=request.POST["address"]
        city=request.POST["city"]
        state=request.POST["state"]
        country=request.POST["country"]
        zipcode = request.POST.get("zipcode")

    
    addressobj=ShippingAddress.objects.get(id=id)
    print(addressobj,"hiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiiii")
    addressobj.address=address
    addressobj.city=city
    addressobj.state=state
    addressobj.country=country
    addressobj.zipcode=zipcode
    addressobj.save()
    return redirect(userprofile)

def removeaddress(request,id):
    item = get_object_or_404(ShippingAddress, id=id)

    # Delete the product
    item.delete()

    # Redirect to a specific URL or view
    return redirect('userprofile') 


def add_address(request):
    if "username" in request.session:
        if request.method == 'POST':
            user = request.session.get('username')
            customerr = customer.objects.get(username=user)
            address = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            country = request.POST.get('country')
            zipcode = request.POST.get('zipcode')

            new_address = ShippingAddress(customer=customerr, address=address, city=city, state=state, country=country, zipcode=zipcode)
            new_address.save()

            return redirect('userprofile')  

    return render(request, 'myapp/userprofile.html')



def deliveredproducts(request):
    if "username" in request.session:
        orderobj = Order.objects.filter(order_status="delivered")
        orderitemobj = OrderItem.objects.filter(order__in=orderobj)

        username = request.session["username"]
        customerobj = customer.objects.get(username=username)
        wishlist_items = Wishlist.objects.filter(customer=customerobj)
        count = wishlist_items.count()
        cart_count = Cart.objects.filter(user=customerobj).count()

        context = {
            'orderobj': orderobj,
            'orderitemobj': orderitemobj,
            'count':count,
            'cart_count':cart_count
        }

        return render(request, "myapp/delivered-products.html", context)

    # Handle the case when "username" is not in the session
    # For example, redirect to a login page or display an error message
    return HttpResponse("Unauthorized access")



def wishlist(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        listobj = Wishlist.objects.filter(customer=user)
        count = listobj.count()
        cart_count = Cart.objects.filter(user=user).count()

    else:
        listobj=[]
        count=0

    context = {
            'listobj':listobj,
            'count':count ,
            'cart_count':cart_count
        }
    return render(request,"myapp/wishlist.html",context)

def before_wishlist(request):
    # if "username" in request.session:
    #     username = request.session["username"]
    #     user = customer.objects.get(username=username)
    #     listobj = Wishlist.objects.filter(customer=user)
    #     count = listobj.count()

    # else:
    #     listobj=[]
    #     count=0

    # context = {
    #         'listobj':listobj,
    #         'count':count 
    #     }
    return render(request,"myapp/before-wishlist.html")






def addtolist(request, product_id):
    if "username" in request.session:
 
        username = request.session.get("username")
        if not username:
            return redirect('login')  # Redirect to the login page if the username is not stored in the session

        user = get_object_or_404(customer, username=username)
        product = get_object_or_404(Products, id=product_id)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",product)
        variant = Productvariant.objects.filter(product=product).first()
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",variant)

        if Wishlist.objects.filter(customer=user, product=product).exists():
            messages.warning(request, "Product already added to wishlist") 
            
            return redirect('userproduct') 
        
        wishlist_item = Wishlist(customer=user, product=product,variant=variant)
        wishlist_item.save()
        return redirect('wishlist')  # Replace 'wishlist' with the actual URL name or path for the wishlist page

def before_addtolist(request, product_id):
    if not "username" in request.session:
 
        username = request.session.get("username")
        if not username:
            return redirect('login')  # Redirect to the login page if the username is not stored in the session

        user = get_object_or_404(customer, username=username)
        product = get_object_or_404(Products, id=product_id)
        print(">>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>",product)
        variant = Productvariant.objects.filter(product=product).first()
        print("<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<<",variant)

        if Wishlist.objects.filter(customer=user, product=product).exists():
            messages.warning(request, "Product already added to wishlist") 
            
            return redirect('product') 
        
        wishlist_item = Wishlist(customer=user, product=product,variant=variant)
        wishlist_item.save()
        return redirect('wishlist')  # Replace 'wishlist' with the actual URL name or path for the wishlist page

     

def removeitem(request,item_id):
    item = get_object_or_404(Wishlist, id=item_id)

    # Delete the product
    item.delete()

    # Redirect to a specific URL or view
    return redirect('wishlist') 

def razorupdateorder(request):
    # totalamount=request.GET["totalamount"]
    username = request.session.get("username")
    user = customer.objects.get(username=username)
    cartobj = Cart.objects.filter(user = user)
    addressid = request.GET.get("addressval")
    address = ShippingAddress.objects.get(id=addressid)
    totalamount=request.GET.get("finalprice")
    
    # totalamount=0
    # for item in cartobj:
    #     totalamount+=item.total

    
           
    date_ordered = date.today()

    orderobj = Order(customer=user,address=address, date_ordered=date_ordered,payment_type="online_payment", total=Decimal(totalamount) )
    orderobj.save()
    

    for item in cartobj:

        product=item.product
        variant=item.variant
        price = item.variant.price
        quantity=item.quantity
        itemtotal = quantity*price

        orderitemobj = OrderItem(product=product,variant=variant, order = orderobj,quantity=quantity, price=price, total=itemtotal )
        orderitemobj.save()

        # orderobj.total += Decimal(item.total)

        item.delete()

    orderobj.save()
    
    

    print("HENNAAAAAAAAAAAAAAAAAAAAAAA",totalamount)


    return JsonResponse({"message":"done"})



from django.template.loader import render_to_string
from django.http import HttpResponse
from xhtml2pdf import pisa
import datetime

def generate_invoice(request,order_id):
    if "username" in request.session:
        # try:
            user = customer.objects.get(username=request.session['username'])
            # ord_id = request.GET.get('order_id')
            ord_id = order_id
            print(ord_id,"????????????????????????????????????????????????????????????")
            ordered_product = Order.objects.get(id=ord_id, customer=user)
            ordered_item = OrderItem.objects.filter(order=ordered_product)
            print(ordered_item,"heyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyyy")

            for item in ordered_item:
                # Access the colors and sizes of each product variant
                variant = item.variant
                colors = variant.color.all()
                sizes = variant.size.all()
                
                item.colors = colors  # Store colors in the item object
                item.sizes = sizes

                for color in colors:
                    colorobj = color.name
                    print(color.name)

                for size in sizes:
                    sizeobj = size.name
                    print(size.name)

            

            data = {
                'date': datetime.date.today(),
                'orderid': ordered_product.id,
                'ordered_date': ordered_product.date_ordered,
                'name': ordered_product.address.customer.name,
                'address': ordered_product.address.address,
                'country': ordered_product.address.country,
                'city': ordered_product.address.city,
                'state': ordered_product.address.state,
                'zipcode': ordered_product.address.zipcode,
                'phone': ordered_product.address.customer.phonenumber,
                # 'product': ordered_item.product.name,
                'amount': ordered_product.total,
                'ordertype': ordered_product.payment_type,
                # 'quantity':ordered_item.quantity,
                'ordered_item':ordered_item,
                "item.colors":item.colors, # Store colors in the item object
                 "item.sizes" :item.sizes,
            }

            template_path = 'invoicepdf.html'
            html = render_to_string(template_path, data)

            # Create a Django response object with PDF content type
            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="Invoice_{data["orderid"]}.pdf"'

            # Create PDF
            pisa_status = pisa.CreatePDF(html, dest=response)
            if pisa_status.err:
                return HttpResponse('We had some errors <pre>' + html + '</pre>')
            return response

        # except (customer.DoesNotExist, Order.DoesNotExist, OrderItem.DoesNotExist):
        #     return HttpResponse('Error: Order not found')
