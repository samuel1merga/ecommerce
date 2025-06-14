from django.urls import path
from . import views

urlpatterns =[
    path('', views.home, name='home'),


    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),

    path('admin/supplier/<int:supplier_id>/approve/', views.approve_supplier, name='approve_supplier'),

    path('admin/supplier/<int:supplier_id>/deactivate/', views.deactivate_supplier, name='deactivate_supplier'),
    path('admin/product/<int:product_id>/delete/', views.delete_product_admin, name='delete_product_admin'),
    path('order/delete/<int:order_id>/', views.delete_order, name='delete_order'),

   path('search/', views.product_search, name='product_search'),


    path('products/', views.product_list, name='product_list'),
    path('product/<int:pk>/', views.product_detail, name='product_detail'),
    path('add-to-cart/<int:pk>/', views.add_to_cart, name='add_to_cart'),
    path('cart/', views.cart, name='cart'),
    path('update-cart/', views.update_cart, name='update_cart'),
    path('remove-from-cart/<int:pk>/', views.remove_from_cart, name='remove_from_cart'),
    path('checkout/', views.checkout, name='checkout'),
    path('process-checkout/', views.process_checkout, name='process_checkout'),
    path('order-confirmation/', views.order_confirmation, name='order_confirmation'),
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('about-us-page/', views.about, name='about'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('my-orders/', views.my_orders, name='my_orders'),
    path('delete/<int:order_id>/', views.delete, name='delete'),

    path('add-product/', views.add_product, name='add_product'),

    path('supplier/register/', views.supplier_register, name='supplier_register'),
    path('supplier/dashboard/', views.supplier_dashboard, name='supplier_dashboard'),
    path('supplier/product/add/', views.add_product, name='add_product'),
    path('supplier/product/<int:product_id>/delete/', views.delete_product, name='delete_product'),
    path('supplier/product/<int:product_id>/edit/',views. edit_product, name='edit_product'),


]
    