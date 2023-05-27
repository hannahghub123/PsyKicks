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
    path("pdetails/<int:someid>",views.pdetails,name="pdetails"),
    path("cart/",views.cart,name="cart"),
]