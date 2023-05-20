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
    
    # Logic to handle logged-in and non-logged-in users
    # obj=Product.object.all()
    #     context = {'obj':obj}

    # return render(request, 'myapp/index.html' , context)
    return render(request,"myapp/index.html")

def products(request):
    return render(request,"myapp/product.html")

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
             return redirect('products')
        
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
        my_user = customer.objects.get(phonenumber=phonenumber)

        if not my_user.uactive:
            messages.info(request, 'Your account has been blocked')
            return redirect('login')
        
        phonenumber = request.POST.get('phonenumber')
        otp = generate_otp()
        
        request.session['U_otp'] = otp
        request.session['U_phone'] = phonenumber
        
        send_otp(phonenumber, otp)
        
        return redirect('otp_verify')
    
    return render(request, 'myapp/otp_login.html') #to enter phn number



def otp_verify(request):
    
    if 'U_otp' in request.session and 'U_phone' in request.session:
        exact_otp = request.session['U_otp']
        phonenumber = request.session['U_phone']

        if request.method == 'POST':
           
            user_otp = request.POST.get('otp')
            if exact_otp == user_otp:
                try:
                    
                    my_user = customer.objects.get(phonenumber=phonenumber)
                    
                    if my_user is not None:

                        request.session['username'] = my_user.username 
                        request.session['phonenumber'] = phonenumber
                        messages.success(request, "Login completed successfully")
                        return redirect('products')
                    
                except customer.DoesNotExist:
                    messages.error(request, "This User doesn't Exist")
            else:
                messages.error(request, "Invalid OTP. Please try again.")

        return render(request, 'verify_otp.html', {'phonenumber': phonenumber})
    
    else:
        return redirect('otp_login')
    

# def add(request):
#     if request.method == "POST":
#         productname = request.POST['productname']
#         description = request.POST['description']
#         quantity = request.POST['quantity']
#         price = request.POST['price']
#         categoryname = request.POST['category']
        

#         categoryobj=category.objects.get(name=categoryname)

#         try:
#             if not all(c.isalpha() or c.isspace() for c in productname):
#                 messages.error(request, "Name should only contain alphabetic characters and spaces!!")
#                 return redirect('admin_index')

            
#             # validate_email(email)
            
             
#             quantity = str(quantity)
#             if not quantity.isdigit() or quantity  < 0 :
#                 raise ValueError("Invalid quantity number!!")
            
#             price = str(price)
#             if not price.isdigit() or price < 0 :
#                 raise ValueError("Invalid price value!!")
        
#             if product.objects.filter(productname = productname, quantity = quantity, category = categoryobj).exists():
#                 raise ValueError("Duplicate entry detected!!")
            
#             if not category.objects.filter(name=categoryname).exists():
#                 raise ValueError("Category Does not exists!!")

            
#         except ValueError as e:
#             messages.error(request,str(e))
#             return redirect('admin_index')
        
#         # except ValidationError:
#         #     messages.error(request, "Invalid email address!!")
#         #     return redirect('admin_index')
        
#         st = product(
#             productname = productname,
#             description = description,
#             quantity = quantity,
#             price = price,
#             category = categoryobj  
#         )
#         st.save()
#         return redirect('admin_index')

#     return render(request,"admin_index.html")

# def edit(request):
#     st = student.objects.all()

#     context = {
#         'st': st,
#     }
    
#     return redirect(request,'admin_index.html',context)

# def update(request,id):

#     if request.method == "POST":
#         name = request.POST['name']
#         image = request.POST['image']
#         email = request.POST['email']
#         batch = request.POST['batch']
#         phone = request.POST['phone']

#         try:
#             if not all(c.isalpha() or c.isspace() for c in name):
#                 messages.error(request, "Name should only contain alphabetic characters and spaces!!")
#                 return redirect('admin_index')

#             validate_email(email)

#             batch = int(batch)
#             if batch < 0 or batch > 2022:
#                 raise ValueError("Invalid batch number!!")
            
#             phone = str(phone)
#             if not phone.isdigit() or len(phone)!=10 :
#                 raise ValueError("Invalid phone number!!")
    

#         except ValueError as e:
#             messages.error(request,str(e))
#             return redirect('admin_index')
        
#         except ValidationError:
#             messages.error(request, "Invalid email address!!")
#             return redirect('admin_index')
        

#         st = student(
#             id = id,
#             name = name,
#             image = image,
#             email = email,
#             batch = batch,
#             phone = phone  
#         )
#         st.save()
#         return redirect('admin_index')

#     return redirect(request,'admin_index.html')

# def delete(request,id):
#     st = student.objects.filter(id=id)
#     st.delete()
    
#     # context ={
#     #     'st':st,
#     # }

#     return redirect('admin_index')
