from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.index,name="index"),
    path("userindex/",views.userindex,name="userindex"),
    path("login/",views.login, name="login"),
    path("signup/",views.signup,name="signup"),
   
    path("otp_login/",views.otp_login,name="otp_login"),
    path("otp_verify/",views.otp_verify,name="otp_verify"),
    path("signout/",views.signout,name="signout"),
    path("product/",views.product,name="product"),
    path("userproduct/",views.userproduct,name="userproduct"),

    path("blog/",views.blog,name="blog"),
    
    path("cart/",views.cart,name="cart"),
    path("usercart/",views.usercart,name="usercart"),
    path("usercheckout/",views.usercheckout, name="usercheckout"),
    path("pdetails/<int:product_id>/",views.pdetails,name="pdetails"),
    path("addtocart/<int:product_id>/",views.addtocart,name="addtocart"),
    path("ordercomplete/",views.ordercomplete,name="ordercomplete"),

]

#    path('update_item/', views.updateItem, name="update_item")
#  path("verify_email/",views.verify_email, name="verify_email"),
