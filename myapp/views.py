import re
from django.shortcuts import render,redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate 
from django.core.exceptions import ValidationError
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
    
        datas = Products.objects.all()

        context={
            'datas':datas,
        }
        return render(request,"myapp/userindex.html",context)


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
    
        my_user = customer.objects.filter(username=username , password=password).count()
        print(my_user,"^^^^^^^^^^^^^^^^^^^^^^")

        if my_user ==1: 
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

        if not username.isalnum():
            error_message["username"] = "Username should be alphanumeric"

        if not name.isalpha():
            error_message["name"] = "Name must be alphabetic."  

        if customer.objects.filter(email=email):
            error_message["email"] = "Email already registered. Please try a different email."

        if not re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email):
            error_message["email"]="Invalid Email"

        if int(phonenumber)<0:
            error_message["phonenumber"] = "phone number should be positive numbers"
        
        if phonenumber==0:
            error_message["phonenumber"] = "invalid phone number"

        if phonenumber.isalpha()==True:
            error_message["phonenumber"] = "Phone number cannot be alphabetic"
        
        if password != confirm_password:
            error_message["password"] = "Passwords doesnot match."
            phonenumber = request.POST['phonenumber']

        if len(password) <3:
            error_message["password"] = "Your password is too weak"

        if error_message:
            return render(request, "myapp/signup.html", {'error_message': error_message,"username":username,"name":name,"email":email,"phonenumber":phonenumber,"password":password,"confirm_password":confirm_password})

        myuser = customer(username =username,name=name,email= email, phonenumber=phonenumber, password=password,isblocked=False)
    
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
    # if "username" in request.session:
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
    
def pdetails(request,someid):
    if "username" in request.session:
        #  and customer.objects.get(username=request.session["username"]).isblocked
        pobj=Products.objects.get(id=someid)
        print("error there")

        return render(request, "myapp/pdetails.html", {"pobj":pobj})
    
    else:
        print("error here")
        return redirect(product)


from django.core.exceptions import ObjectDoesNotExist

def cart(request):
    
    if request.user.is_authenticated:
        try:
            customer_instance = customer.objects.get(username=request.session['username'])
            order = Order.objects.filter(customer=customer_instance, complete=False).first()
            if order is not None:
                items = order.orderitem_set.all()
            else:
                items = []
        except ObjectDoesNotExist:
            items = []
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}
       

    context = {'items': items, 'order': order}
    return render(request, "myapp/cart.html", context)

def usercart(request):
    items = []
    order = None
    if 'username' in request.session:
        try:
            customer_instance = customer.objects.get(username=request.session['username'])
            order = Order.objects.filter(customer=customer_instance, complete=False).first()
            if order is not None:
                items = order.orderitem_set.all()
            else:
                items = []
                print("yesss1")
        except ObjectDoesNotExist:
            items = []
            print("yesss2")
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    context = {'items': items, 'order': order}
    return render(request, "myapp/usercart.html", context)


def usercheckout(request):
    items = []
    order = None
    if 'username' in request.session:
        try:
            customer_instance = customer.objects.get(username=request.session['username'])
            order = Order.objects.filter(customer=customer_instance, complete=False).first()
            if order is not None:
                items = order.orderitem_set.all()
            else:
                items = []
                print("yesss1")
        except ObjectDoesNotExist:
            items = []
            print("yesss2")
    else:
        items = []
        order = {'get_cart_total':0, 'get_cart_items':0}

    context = {'items': items, 'order': order}
    return render(request,"myapp/checkout.html", context)