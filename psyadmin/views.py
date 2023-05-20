from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from myapp.models import *
# from .models import MyAdmin

def admin_index(request):
    if 'adminuser' in request.session:
        return render(request, "psyadmin/admin-index.html")
    else:
        return redirect('admin_login')
    
def admin_login(request):
    if 'adminuser' in request.session:
        return redirect('admin_index')
    
    if request.method == 'POST':
        adminuser = request.POST['adminuser']
        adminpass = request.POST['adminpass']

        user = authenticate(request, username=adminuser, password=adminpass)
        
        if user is not None:
            login(request, user)
            request.session['adminuser'] = adminuser
            return redirect('admin_index')
        else:
            error_message = 'Invalid username or password!'
    
    return render(request, 'psyadmin/admin-login.html')

def admin_products(request):
    return render(request,"psyadmin/admin-products.html")

def admin_addproducts(request):
    if request.method == "POST":
        productname = request.POST['productname']
        description = request.POST['description']
        quantity = request.POST['quantity']
        price = request.POST['price']
        categoryname = request.POST['category']
        

        categoryobj=category.objects.get(name=categoryname)

        try:
            if not all(c.isalpha() or c.isspace() for c in productname):
                error_message = ( "Name should only contain alphabetic characters and spaces!!")
                return redirect('admin_index')

            
            # validate_email(email)
            
             
            quantity = str(quantity)
            if not quantity.isdigit() or quantity  < 0 :
                raise ValueError("Invalid quantity number!!")
            
            price = str(price)
            if not price.isdigit() or price < 0 :
                raise ValueError("Invalid price value!!")
        
            if product.objects.filter(productname = productname, quantity = quantity, category = categoryobj).exists():
                raise ValueError("Duplicate entry detected!!")
            
            if not category.objects.filter(name=categoryname).exists():
                raise ValueError("Category Does not exists!!")

            
        except ValueError as e:
            error_message =(str(e))
            return redirect('admin_index')
        
        # except ValidationError:
        #     messages.error(request, "Invalid email address!!")
        #     return redirect('admin_index')
        
        st = product(
            productname = productname,
            description = description,
            quantity = quantity,
            price = price,
            category = categoryobj  
        )
        st.save()
        return redirect('admin_index')

    return render(request,"psyadmin/admin-products.html")

