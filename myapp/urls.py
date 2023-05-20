from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.index,name="index"),
    path("products/",views.products,name="products"),
    path("login/",views.login, name="login"),
    path("signup/",views.signup,name="signup"),
    path("otp_login/",views.otp_login,name="otp_login"),
    path("otp_verify/",views.otp_verify,name="otp_verify"),
  
]