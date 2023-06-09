from django.core.exceptions import ObjectDoesNotExist
import re
from django.shortcuts import get_object_or_404, render,redirect
from django.contrib import messages
from decimal import Decimal
from django.views import View
import requests
import random
from . models import *
from .forms import *

# Create your views here.
def index(request):
     
    datas = Products.objects.all()
    
    context={
        'datas':datas,
    }
    return render(request,"myapp/index.html",context)
     
def userindex(request):
    if request.user.is_authenticated:
        username = request.session["username"]
        user = customer.objects.get(username=username)

        orders = Order.objects.filter(customer=user, complete=False)
        if orders.exists():
            order = orders.first()
        else:
            order = Order.objects.create(customer=user, complete=False)

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
    gender = Gender.objects.all()
    
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')
    selected_gender = request.GET.get('gender')

    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)
    if selected_color:
        datas = datas.filter(color__name=selected_color)
    if selected_size:
        datas = datas.filter(size__name=selected_size)
    if selected_gender:
        datas = datas.filter(gender__name=selected_gender)



    context = {
        'datas': datas,
        'cartItems': cartItems,
        'colors': colors,
        'category': category,
        'brand': brand,
        'size': size,
        'gender':gender,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
        'selected_color':selected_color,
    }

    return render(request, "myapp/userindex.html", context)




def signout(request):
    if 'username' in request.session:
        # del request.session['username']
        request.session.flush()
    return redirect('index')



def login(request):

    error_message = {}
    
    
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

            
    return render(request,"myapp/login.html")


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
        gender = Gender.objects.all()

        # if request.method=="POST":
        #     enteredproduct=request.POST.get("searchitem")
        #     datas=Products.objects.filter(name=enteredproduct)
        #     return render(request,"myapp/userproduct.html",{"datas":datas})
        
    selected_category = request.GET.get('category')  # Get the selected category from the query parameters
    selected_brand = request.GET.get('brand')
    selected_color = request.GET.get('color')
    selected_size = request.GET.get('size')
    selected_gender = request.GET.get('gender')

    if selected_category:
        datas = datas.filter(category__name=selected_category)
    if selected_brand:
        datas = datas.filter(brand__name=selected_brand)
    if selected_color:
        datas = datas.filter(color__name=selected_color)
    if selected_size:
        datas = datas.filter(size__name=selected_size)
    if selected_gender:
        datas = datas.filter(gender__name=selected_gender)

    context = {
        'datas': datas,
        'category':category,
        'colors':colors,
        'brand':brand,
        'size':size,
        'gender':gender,
        'selected_category': selected_category,
        'selected_brand':selected_brand,
        'selected_color':selected_color,
    }

    return render(request,"myapp/userproduct.html",context)
    # else:
        # return redirect(userindex)
    
def product(request):
  
        datas=Products.objects.all()

        # if request.method=="POST":
            # enteredproduct=request.POST.get("searchitem")
            # datas=Products.objects.filter(name=enteredproduct)
            # return render(request,"myapp/userproduct.html",{"datas":datas})
        
        return render(request,"myapp/product.html",{"datas":datas})
        # else:
        #     return redirect(userindex)
    
def blog(request):
    return render(request,"myapp/blog.html")

def contact(request):
    return render(request,"myapp/contact.html")

def about(request):
    return render(request,"myapp/about.html")


def pdetails(request, product_id):
    if request.method=="POST":
        quantity=request.POST.get("quantity")
        pdtobj=Products.objects.get(id=product_id)
        print(quantity,"HHHHHHHHHHHHHHH")
        username=request.session.get("username")
        user=customer.objects.get(username=username)
        total=Decimal(quantity)*pdtobj.price
        
        if pdtobj in Cart.user:
            quantity += quantity
            cartobj=Cart.user(quantity=quantity,total=total)
            cartobj.save()
        else:
            cartobj=Cart(user=user,product=pdtobj,quantity=quantity,total=total)
            cartobj.save()

    product = Products.objects.prefetch_related('images').filter(id=product_id).first()
    images = product.images.all() if product else []
    products_in_same_category = Products.objects.filter(category=product.category)
    
    return render(request, 'myapp/product-detail.html', {
        'product': product,
        'images': images,
        'products_in_same_category': products_in_same_category
    })

def user_pdetails(request, product_id):
    if request.method == "POST":
        quantity = int(request.POST.get("quantity"))
        pdtobj = Products.objects.get(id=product_id)
        username = request.session.get("username")
        user = customer.objects.get(username=username)
        total = Decimal(quantity) * pdtobj.price
        
        try:
            # Check if the product is already in the cart
            cartobj = Cart.objects.get(user=user, product=pdtobj)
            cartobj.quantity += quantity  # Increase the quantity
            cartobj.total += total  # Update the total
            cartobj.save()
        except Cart.DoesNotExist:
            cartobj = Cart(user=user, product=pdtobj, quantity=quantity, total=total)
            cartobj.save()

    product = Products.objects.prefetch_related('images').filter(id=product_id).first()
    images = product.images.all() 
    products_in_same_category = Products.objects.filter(category=product.category)
    
    return render(request, 'myapp/user-pdetails.html', {
        'product': product,
        'images': images,
        'products_in_same_category': products_in_same_category
    })



def addtocart(request, product_id):
    if request.method == "POST":
        if "username" in request.session:
            
            username = request.session["username"]
            user = customer.objects.get(username=username)
        
            product = Products.objects.get(id=product_id)
            # quantity = request.POST.get("quantity")


            cartobjs=Cart.objects.filter(user=user)
            # for item in cartobjs:
            #     if item.product==product:
            #         item.quantity+=int(quantity)
            #         item.save()
            #         return redirect('usercart') 

            
            for item in cartobjs:
                if item.product==product:
                    return redirect ('userproduct')
            cartobj = Cart(user=user, product=product,total=product.price*product.quantity, quantity=1)
            cartobj.save()
            return redirect('usercart') 
        else:
            return redirect('login') 

    return redirect('userproduct')


def cart(request):
    if "username" in request.session:
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
       
        quantsum=0
        total_price=0

        for item in cartobj:
            quantsum+=item.quantity
            total_price += item.product.price * item.quantity

    

        datas = {
            'cartobj': cartobj,
             "total_price":total_price,
            "quantsum":quantsum
        }
        return render(request, "myapp/usercart.html", datas)
    else:
        return render(request, "myapp/userindex.html")
    
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
        username = request.session.get("username")  # Use get() with a default value of None
        if username is None:
            return redirect("login")
        user = customer.objects.get(username=username)
        cartobj = Cart.objects.filter(user=user)

        quantsum = 0
        total_price = 0
        for item in cartobj:
            quantsum += item.quantity
            total_price += item.product.price * item.quantity

        coupon = request.POST.get("coupon")
        coupon_obj = Coupon.objects.filter(coupon_code=coupon).first()

        if coupon_obj and total_price > coupon_obj.minimum_amount and not any(item.coupon for item in cartobj):
            # Check if the coupon has been applied to any other orders by the user
            if Order.objects.filter(customer=user, cart__coupon=coupon_obj).exists():
                error_message = "Coupon already applied to another order."
                context = {
                    "error_message": error_message,
                    "cartobj": cartobj,
                    "quantsum": quantsum,
                    "total_price": total_price,
                }
                return render(request, "myapp/checkout.html", context)

            total_price -= coupon_obj.discount_price

        context = {
            "cartobj": cartobj,
            "quantsum": quantsum,
            "total_price": total_price,
        }

    if request.method == "POST":
        if "addressbutton" in request.POST:

            error_message = {}
            username = request.POST.get("username")
            email = request.POST.get("email")
            address = request.POST.get("address")
            city = request.POST.get("city")
            state = request.POST.get("state")
            zipcode = request.POST.get("zipcode")
            country = request.POST.get("country")

            if len(username) > 10:
                error_message["username"] = "Username must be under 10 characters."
            if not username.isalpha():
                error_message["username"] = "Name must be alphabetic."
            if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
                error_message["email"] = "Invalid Email"

            if not country.isalpha():
                error_message["country"] = "Country name should be alphabetic"
            if len(country) < 5:
                error_message["country"] = "Country name should contain a minimum of five characters"
            if not state.isalpha():
                error_message["state"] = "State name can't have numbers"
            if len(state) < 3:
                error_message["state"] = "State name should contain a minimum of three characters"
            if not city.isalpha():
                error_message["city"] = "City name should be alphabetic"
            if len(city) < 5:
                error_message["city"] = "District name should contain a minimum of five characters"
            if len(address) < 5:
                error_message["address"] = "House name should contain a minimum of three characters"
            if not all(c.isalnum() or c.isspace() for c in username):
                error_message["name"] = "Invalid string entry"
            if zipcode.isalpha():
                error_message["zipcode"] = "Zipcode can't have alphabets"
            if len(zipcode) != 6:
                error_message["zipcode"] = "Invalid Zipcode"

            if error_message:
                data = {
                    "error_message": error_message,
                    "username": username,
                    "email": email,
                    "country": country,
                    "address": address,
                    "city": city,
                    "state": state,
                    "zipcode": zipcode,
                    "cartobj": cartobj,
                    "total_price": total_price,
                    "quantsum": quantsum,
                }
                return render(request, "myapp/checkout.html", data)

            address_details = ShippingAddress(
                customer=user,
                address=address,
                city=city,
                state=state,
                zipcode=zipcode,
                country=country,
            )
            address_details.save()
            data = {
                "username": username,
                "email": email,
                "country": country,
                "address": address,
                "city": city,
                "state": state,
                "zipcode": zipcode,
                "cartobj": cartobj,
                "total_price": total_price,
                "quantsum": quantsum,
            }
            return render(request, "myapp/checkout.html", data)

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
    return render(request,"myapp/ordercomplete.html") 


def userprofile(request):
    username = request.session["username"]
    customerobj = customer.objects.get(username=username)

    orderobjs = Order.objects.filter(customer=customerobj).select_related('cart__product')
    
    addressobjs = ShippingAddress.objects.filter(customer=customerobj)

    context = {
        "orderobjs": orderobjs,
        "username": username,
        "addressobjs": addressobjs,
        "customerobj": customerobj
    }

    return render(request, "myapp/userprofile.html", context)


def updateuser(request):
    if request.method=="POST":
        name=request.POST["name"]
        name=request.POST["name"]
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
    addressobj.address=address
    addressobj.city=city
    addressobj.state=state
    addressobj.country=country
    addressobj.zipcode=zipcode
    addressobj.save()
    return redirect(userprofile)

def deliveredproducts(request):
    pass

def wishlist(request):
    listobj = Wishlist.objects.all()

    context = {
        'listobj':listobj,
    }
    return render(request,"myapp/wishlist.html",context)




# def addtolist(request, product_id):
#     if request.method == "POST":
#         if "username" in request.session:
#             username = request.session["username"]
#             user = customer.objects.get(username=username)
        
#             product = Products.objects.get(id=product_id)
          
#             wishlist_obj, created = Wishlist.objects.get_or_create(customer=user, product=product)
#             if created:
#                 return redirect('wishlist')  
#             else:
#                 return redirect('userproduct') 
#         else:
#             return redirect('login')  

    
#     return redirect('userproduct')  




def addtolist(request, product_id):
    error_message={}
    username = request.session.get("username")
    if not username:
        return redirect('login')  # Redirect to the login page if the username is not stored in the session

    user = get_object_or_404(customer, username=username)
    product = get_object_or_404(Products, id=product_id)

    # if Wishlist.objects.filter(customer=user, product=product).exists():
    #     error_message["product"] = "Product already added to wishlist"
    #     # You can pass the error_message to the template or handle it as desired
    #     return redirect('userproduct')  # Replace 'wishlist' with the actual URL name or path for the wishlist page

    wishlist_item = Wishlist(customer=user, product=product)
    wishlist_item.save()
    return redirect('wishlist')  # Replace 'wishlist' with the actual URL name or path for the wishlist page

        
   

def removeitem(request,item_id):
    item = get_object_or_404(Wishlist, id=item_id)

    # Delete the product
    item.delete()

    # Redirect to a specific URL or view
    return redirect('wishlist') 