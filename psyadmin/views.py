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
            error = 'Invalid username or password!'
            return render(request,"psyadmin/admin-login.html",{"error":error})

    
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
    

def addproducts(request):
    categoryobjs=Category.objects.all()
    if request.method=="POST":
        name=request.POST.get("name")
        price=request.POST.get("price")
        quantity=request.POST.get("quantity")
        category_name=request.POST.get("category")
        description=request.POST.get("description")
        image1=request.FILES.get("image1")
        image2=request.FILES.get("image2")
        image3=request.FILES.get("image3")
        image4=request.FILES.get("image4")

        if len(name)<4:
            error="Productname should contain minimum four characters"
        elif len(name)>20:
            error="Username can only have upto 20 characters"
        elif name.isalpha()==False:
            error="Productname can't have numbers" 
        elif price.isalpha()==True:
            error="Price can't have letters"
        elif quantity.isalpha()==True:
            error="Quantity can't have letters"
        elif category_name.isalpha==False:
            error="Category field can't have numbers"
        elif category_name not in Category.objects.filter(name=category_name).values_list('name', flat=True):
            error="Invalid category"
        elif len(description)<4:
            error="Description should contain minimum four characters"
        else:
            categoryobject=Category.objects.get(name=category_name)
            productitems = Products.objects.create(
            name=name,
            category=categoryobject,
            description=description,
            quantity=quantity,
            price=price,
            image1=image1,
            image2=image2,
            image3=image3,
            image4=image4)            
            # newproduct=Products(name=name,price=price,quantity=quantity,category=categoryobject,description=description,image1=image1,image2=image2,image3=image3,image4=image4)
            # newproduct.save()
            return redirect(products)
        if error:
            return render(request,"psyadmin/add-products.html",{"error":error,"categoryobjs":categoryobjs})

    return render(request,"psyadmin/add-products.html",{"categoryobjs":categoryobjs})
    

def editproducts(request, someid):
    content=Products.objects.get(id=someid)
    categoryobjs=Category.objects.all()

    if request.method == 'POST':
        name=request.POST.get("name")
        price=request.POST.get("price")
        quantity=request.POST.get("quantity")
        category_name=request.POST.get("category")
        # image1=request.FILES.get("image")
        # print(image1,"******")
        description=request.POST.get("description")
        if len(name)<4:
            error="Productname should contain minimum four characters"
        elif len(name)>20:
            error="Username can only have upto 20 characters"
        elif name.isalpha()==False:
            error="Productname can't have numbers" 
        elif price.isalpha()==True:
            error="Price can't have letters"
        elif quantity.isalpha()==True:
            error="Quantity can't have letters"
        # elif category.isalpha==False:
        #     error="Category field can't have numbers"
        elif len(description)<4:
            error="Description should contain minimum four characters"
        else:

            content.name = request.POST.get('name')
            content.description = request.POST.get('description')
            content.price = request.POST.get('price')
            content.quantity=quantity

            # Check if new images are provided
            if 'image1' in request.FILES:
                # Delete the existing image1 file
                if content.image1:
                    os.remove(content.image1.path)
                content.image1 = request.FILES.get('image1')

            if 'image2' in request.FILES:
                # Delete the existing image2 file
                if content.image2:
                    os.remove(content.image2.path)
                content.image2 = request.FILES.get('image2')

            if 'image3' in request.FILES:
                # Delete the existing image3 file
                if content.image3:
                    os.remove(content.image3.path)
                content.image3 = request.FILES.get('image3')

            if 'image4' in request.FILES:
                # Delete the existing image3 file
                if content.image4:
                    os.remove(content.image4.path)
                content.image4 = request.FILES.get('image4')

            # category_name = request.POST.get('category')

            # Retrieve the category if it exists, otherwise assign a default category
            categoryobject=Category.objects.get(name=category_name)

            content.category = categoryobject

            content.save()
            return redirect(products)
        
        if error:
            return render(request,"psyadmin/edit-products.html",{"content":content,"error":error,"categoryobjs":categoryobjs})

    return render(request,"psyadmin/edit-products.html",{"content":content,"categoryobjs":categoryobjs})

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
    error = None

    if request.method == "POST":
        name = request.POST.get("name")
        stock = request.POST.get("stock")

        if len(name) == 0:
            error = "Category name field can't be empty"
        elif not name.isalpha():
            error = "Category name can't contain numbers"
        elif len(name) < 4:
            error = "Category name should have at least 4 letters"
        elif len(name) > 20:
            error = "Category name can have at most 20 letters"
        else:
            category = Category(name=name, stock=stock)
            category.save()
            return redirect('categories')

    return render(request, "psyadmin/addcategories.html", {"datas": datas, "error": error})



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




