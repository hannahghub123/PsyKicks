from django.urls import path
from . import views

urlpatterns = [
    
  path("",views.admin_index,name="admin_index"),
  path("admin_login/",views.admin_login,name="admin_login"), 
  path("admin_logout/",views.admin_logout,name="admin_logout"), 
  path("products/",views.products, name="products"),
  path("productvariant/<int:item_id>/",views.productvariant,name="productvariant"),
  path("add_productvariant/",views.add_productvariant,name="add_productvariant"),
  path("addproducts/",views.addproducts, name="addproducts"),
  path("editproducts/<int:someid>",views.editproducts, name="editproducts"),
  path("deleteproducts/<int:someid>",views.deleteproducts, name="deleteproducts"),
  path("categories/",views.categories, name="categories"),
  path("editcategories/<int:someid>",views.editcategories, name="editcategories"),
  path("addcategories/",views.addcategories, name="addcategories"),
  
  path("users/",views.users,name="users"),
  path("blockuser/<int:someid>",views.blockuser,name="blockuser"),
  path("unblockuser/<int:someid>",views.unblockuser,name="unblockuser"),

  path("blockcategory/<int:someid>",views.blockcategory,name="blockcategory"),
  path("unblockcategory/<int:someid>",views.unblockcategory,name="unblockcategory"),

  path('orders/', views.orders, name='orders'),
  path('orderitems/<int:item_id>', views.orderitems, name='orderitems'),
  path('update_orderstatus/<int:item_id>', views.update_orderstatus, name='update_orderstatus'),

  path('coupon_management/',views.coupon_management,name="coupon_management"),
  path("add_coupon/",views.add_coupon, name="add_coupon"),
  
  path("is_expired/<int:someid>",views.is_expired,name="is_expired"),
  path("available/<int:someid>",views.available,name="available"),

  path("productoffer/",views.productoffer,name="productoffer"),
  path("productoffer_is_expired/<int:someid>",views.productoffer_is_expired,name="productoffer_is_expired"),
  path("productoffer_available/<int:someid>",views.productoffer_available,name="productoffer_available"),
  path("addnew_productoffer/",views.addnew_productoffer,name="addnew_productoffer"),
  

  path("categoryoffer/",views.categoryoffer,name="categoryoffer"),
    path("categoryoffer_is_expired/<int:someid>",views.categoryoffer_is_expired,name="categoryoffer_is_expired"),
  path("categoryoffer_available/<int:someid>",views.categoryoffer_available,name="categoryoffer_available"),
  path("addnew_categoryoffer/",views.addnew_categoryoffer, name="addnew_categoryoffer"),

]

  