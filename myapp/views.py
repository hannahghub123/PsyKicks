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
     if 'adminuser' in request.session:
        datas = Products.objects.all()

        context={
            'datas':datas,
        }
        return render(request,"myapp/index.html",context)

def product(request):
    if "adminuser" in request.session:
        datas=Products.objects.all()

        if request.method=="POST":
            enteredproduct=request.POST.get("searchitem")
            datas=Products.objects.filter(name=enteredproduct)
            return render(request,"myapp/product.html",{"datas":datas})
        
        return render(request,"myapp/product.html",{"datas":datas})
    else:
        return redirect(index)

def signout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('index')
    
    

def login(request):
    
    if 'username' in request.session:
        return redirect('index')
    
    if request.method =='POST':
        username = request.POST['username']
        password = request.POST['password']
    
        my_user = authenticate(request,username=username , password=password)

        if my_user is not None: 
            messages.info(request, 'Successfully logged in')
            request.session['username'] = username
            return redirect('index')
           
        else:
             messages.info(request, 'Enter valid username and password!!')
             return redirect('product')
        
    return render(request,"myapp/login.html")

def signup(request):
    if request.method == "POST":

        username = request.POST['username']
        name = request.POST['name']
        email = request.POST['email']
        phonenumber = request.POST['phonenumber']
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        if customer.objects.filter(username=username):
            error_message = "Username already exists. Please try a different username."
            return render(request, "myapp/signup.html", {'error_message': error_message})

        if customer.objects.filter(email=email):
            error_message = "Email already registered. Please try a different email."
            return render(request, "myapp/signup.html", {'error_message': error_message})

        if len(username) > 10:
            error_message = "Username must be under 10 characters."
            return render(request, "myapp/signup.html", {'error_message': error_message})

        if not username.isalnum():
            error_message = "Username must be alphanumeric."
            return render(request, "myapp/signup.html", {'error_message': error_message})
        
        if not name.isalpha():
            error_message = "Name must be alphabetic."
            return render(request, "myapp/signup.html", {'error_message': error_message})

        if password != confirm_password:
            error_message = "Passwords don't match."
            return render(request, "myapp/signup.html", {'error_message': error_message})

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
            messages.info(request, 'Your account has been blocked')
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
                        return redirect('product')
                except customer.DoesNotExist:
                    messages.error(request, "This User doesn't Exist")
            else:
                messages.error(request, "Invalid OTP. Please try again.")
        return render(request, 'myapp/verify_otp.html', {'phonenumber': phonenumber})
    else:
        return redirect('otp_login')
    
def pdetails(request,someid):
    if "username" in request.session and customer.objects.get(username=request.session["username"]).isblocked:
        pobj=Products.objects.get(id=someid)
        print("error there")

        return render(request, "myapp/pdetails.html", {"pobj":pobj})
    
    else:
        print("error here")
        return redirect(product)

def signout(request):
    if 'username' in request.session:
        del request.session['username']
    return redirect('index')