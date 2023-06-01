import re
from django.shortcuts import render,redirect
from django.contrib import messages
import requests
import random
from . models import *

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
    context = {
        'datas': datas,
        'cartItems': cartItems,
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

       
        myuser = customer(username=username, name=name, email=email, phonenumber=phonenumber, password=password, isblocked=False)
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
        
        user = customer.objects.get(phonenumber=phonenumber)
        
        if user.isblocked:
            error_message = "Your account has been blocked"
            return redirect('login')
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

        # if request.method=="POST":
        #     enteredproduct=request.POST.get("searchitem")
        #     datas=Products.objects.filter(name=enteredproduct)
        #     return render(request,"myapp/userproduct.html",{"datas":datas})
        
        return render(request,"myapp/userproduct.html",{"datas":datas})
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
    

from decimal import Decimal

def pdetails(request, product_id):
    product = Products.objects.prefetch_related('images').filter(id=product_id).first()
    images = product.images.all() if product else []
    products_in_same_category = Products.objects.filter(category=product.category)
    
    return render(request, 'myapp/product-detail.html', {
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
            quantity = request.POST.get("quantity")
            if quantity:
                quantity = int(quantity)
                total = Decimal(quantity) * product.price
                cartobj = Cart(user=user, product=product, total=total, quantity=quantity)
                cartobj.save()
                return redirect('usercart')  # Replace 'cart' with the appropriate URL name for your cart view
        else:
            return redirect('login')  # Replace 'login' with the appropriate URL name for your login view

    # Handle the case where the request method is not POST or if the username is not in the session
    return redirect('userproduct')  # Replace 'product_details' with the appropriate URL name for your product details view


def cart(request):
    if "username" in request.session:
        cartobj = Cart.objects.all()

        datas = {
            'cartobj' : cartobj
        }

        return render(request, "myapp/cart.html", datas)
    
from django.db.models import Sum

def usercart(request):
    if "username" in request.session:
        username = request.session["username"]
        user = customer.objects.get(username=username)
        cartobj = Cart.objects.filter(user=user)
        quantsum=0
        for item in cartobj:
            quantsum+=item.quantity
        total = cartobj.aggregate(total=Sum('total'))['total']
        datas = {
            'cartobj': cartobj,
            'total': total,
            "quantsum":quantsum
        }
        return render(request, "myapp/usercart.html", datas)
    else:
        return render(request, "myapp/userindex.html")

def usercheckout(request):
    if customer.objects.get(username=request.session["username"]).isblocked:
        return redirect(login)

    if "username" in request.session :
        username = request.session["username"]
        user = customer.objects.get(username=username)
        cartobj = Cart.objects.filter(user=user)
        totalsum = 0
        count = 0
        for item in cartobj:
            totalsum += item.total
            count += 1
        context = {"totalsum": totalsum, "count": count, 'cartobj': cartobj}
        

    if request.method == "POST":
              
            
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
                if not address.isalpha():
                    error_message["address"] = "Address should be alphabetic"
                if zipcode.isalpha():
                    error_message["zipcode"] = "Zipcode can't have alphabets"
                if len(zipcode) != 6:
                    error_message["zipcode"] = "Invalid Zipcode"
                
                if error_message:
                    datas = {
                        "error_message": error_message,
                        "username": username,
                        "email": email,
                        "country": country,
                        "address": address,
                        "city": city,
                        "state": state,
                        "zipcode": zipcode,
                        "totalsum": totalsum, "count": count, 'cartobj': cartobj
                    }
                    
                    return render(request, "myapp/checkout.html", datas)

                address_details = ShippingAddress(customer=user, address=address, city=city, state=state,
                                                zipcode=zipcode, country=country)
                address_details.save()
                # requser=Cart.objects.get(user=user)
                # orderobj=Order(cart=cartobj,customer=requser,complete=True,transaction_id="ddd")
                # orderobj.save()
                    
                    


                



                
                
                return redirect('ordercomplete')  # Redirect to the appropriate view or provide correct arguments

                
    return render(request, "myapp/checkout.html", context)


  
def ordercomplete(request):
    return render(request,"myapp/ordercomplete.html") 


