from django.urls import path
from . import views

urlpatterns = [
    
  path("",views.admin_index,name="admin_index"),
  path("admin_login/",views.admin_login,name="admin_login"), 
  path("admin_logout/",views.admin_logout,name="admin_logout"), 
  path("products/",views.products, name="products"),
  path("addproducts/",views.addproducts, name="addproducts"),
  path("editproducts/<int:someid>",views.editproducts, name="editproducts"),
  path("deleteproducts/<int:someid>",views.deleteproducts, name="deleteproducts"),
  path("categories/",views.categories, name="categories"),
  path("editcategories/<int:someid>",views.editcategories, name="editcategories"),
  path("addcategories/",views.addcategories, name="addcategories"),
  path("deletecategories/<int:someid>",views.deletecategories, name="deletecategories"),
  path("users/",views.users,name="users"),
  path("blockuser/<int:someid>",views.blockuser,name="blockuser"),
  path("unblockuser/<int:someid>",views.unblockuser,name="unblockuser"),

  path("blockcategory/<int:someid>",views.blockcategory,name="blockcategory"),
  path("unblockcategory/<int:someid>",views.unblockcategory,name="unblockcategory"),

]

  