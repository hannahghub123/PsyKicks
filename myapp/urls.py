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
    path("contact/",views.contact,name="contact"),
    path("about/",views.about,name="about"),
    
    path("cart/",views.cart,name="cart"),
    path("usercart/",views.usercart,name="usercart"),
    path("usercheckout/",views.usercheckout, name="usercheckout"),
    path("pdetails/<int:product_id>/",views.pdetails,name="pdetails"),
    path("user_pdetails/<int:product_id>/",views.user_pdetails,name="user_pdetails"),
    path('addtocart/<int:product_id>/', views.addtocart, name='addtocart'),
    path('list_addtocart/<int:product_id>/', views.list_addtocart, name='list_addtocart'),
    path('removecartitem/<int:item_id>/', views.removecartitem, name='removecartitem'),
    path('remove_coupon/<int:coupon_id>/', views.remove_coupon, name='remove_coupon'),

   
    path("ordercomplete/",views.ordercomplete,name="ordercomplete"),
    path("userprofile/",views.userprofile,name="userprofile"),
    path("updateuser/",views.updateuser,name="updateuser"),
    path("editaddress/<int:id>/",views.editaddress,name="editaddress"),
    path("deliveredproducts/",views.deliveredproducts,name="deliveredproducts"),

    path("wishlist/",views.wishlist,name="wishlist"),
    path("addtolist/<int:product_id>/",views.addtolist,name="addtolist"),
    path('removeitem/<int:item_id>/', views.removeitem, name='removeitem'),

    
  
]

#    path('update_item/', views.updateItem, name="update_item")
#  path("verify_email/",views.verify_email, name="verify_email"),
