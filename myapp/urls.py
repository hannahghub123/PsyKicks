from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    
    path("",views.index,name="index"),
    path("userindex/",views.userindex,name="userindex"),
    
    path("signup/",views.signup,name="signup"),
    path("login/",views.login, name="login"),
    path("otp_login/",views.otp_login,name="otp_login"),
    path("otp_verify/",views.otp_verify,name="otp_verify"),
    path("signout/",views.signout,name="signout"),

    path("product/",views.product,name="product"),
    path("pdetails/<int:product_id>/",views.pdetails,name="pdetails"),
    path("userproduct/",views.userproduct,name="userproduct"),
    path("user_pdetails/<int:product_id>/",views.user_pdetails,name="user_pdetails"),

    path("blog/",views.blog,name="blog"),
    path("before_blog/",views.before_blog,name="before_blog"),
    path("contact/",views.contact,name="contact"),
    path("before_contact/",views.before_contact,name="before_contact"),
    path("about/",views.about,name="about"),
    path("before_about/",views.before_about,name="before_about"),
    
    path("cart/",views.cart,name="cart"),
    path("usercart/",views.usercart,name="usercart"),
    # path('addtocart/<int:product_id>/', views.addtocart, name='addtocart'),
    path('quantity_inc/<int:item_id>/',views.quantity_inc,name="quantity_inc"),
    path('quantity_dec/<int:item_id>/',views.quantity_dec,name="quantity_dec"),
    path('removecartitem/<int:item_id>/', views.removecartitem, name='removecartitem'),

    path("usercheckout/",views.usercheckout, name="usercheckout"),
    path('remove_coupon/<int:coupon_id>/', views.remove_coupon, name='remove_coupon'),
    path("ordercomplete/",views.ordercomplete,name="ordercomplete"),
    path("wallet/",views.wallet,name="wallet"),
   
    path("userprofile/",views.userprofile,name="userprofile"),
    path("before_userprofile/",views.before_userprofile,name="before_userprofile"),
    path("updateuser/",views.updateuser,name="updateuser"),
    path("editaddress/<int:id>/",views.editaddress,name="editaddress"),
    path("removeaddress/<int:id>/",views.removeaddress,name="removeaddress"),
    path('add_address/', views.add_address, name='add_address'),
    path("deliveredproducts/",views.deliveredproducts,name="deliveredproducts"),
    path("user_orders/",views.user_orders,name="user_orders"),
    path("orderdetails/<int:item_id>/",views.orderdetails,name="orderdetails"),
    path("cancel_order/<int:order_id>/",views.cancel_order,name="cancel_order"),
    path("return_order/<int:order_id>/",views.return_order,name="return_order"),

    path("wishlist/",views.wishlist,name="wishlist"),
    path("before_wishlist/",views.before_wishlist,name="before_wishlist"),
    path("addtolist/<int:product_id>/",views.addtolist,name="addtolist"),
    path("before_addtolist/<int:product_id>/",views.before_addtolist,name="before_addtolist"),
    path('list_addtocart/<int:product_id>/', views.list_addtocart, name='list_addtocart'),
    path('removeitem/<int:item_id>/', views.removeitem, name='removeitem'),
    
    
    path("updatevariant/",views.updatevariant,name="updatevariant"),
    path("generate_invoice/<int:order_id>/",views.generate_invoice,name="generate_invoice"),
    path("razorupdateorder/",views.razorupdateorder,name="razorupdateorder"),

]

#    path('update_item/', views.updateItem, name="update_item")
#  path("verify_email/",views.verify_email, name="verify_email"),
