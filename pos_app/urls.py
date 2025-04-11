from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('logout/', views.logout, name='logout'),
    path('register/', views.register, name='register'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),

    # User management paths
    path('dashboard/add_user/', views.add_user, name='add_user'),
    #path('dashboard/update_user/', views.update_user, name='update_user'), 
    path('dashboard/update_user/<int:user_id>/', views.update_user, name='update_user'),
    path('dashboard/delete_user/', views.delete_user, name='delete_user'),

    # Product management paths
    path('dashboard/add_product/', views.add_product, name='add_product'),
    #path('dashboard/update_product/', views.update_product, name='update_product'),
    #path('dashboard/update_product/<int:product_id>/', views.update_product, name='update_product'),
    path("dashboard/get_product/<int:product_id>/", views.get_product, name="get_product"),
    path("dashboard/update_product/<int:product_id>/", views.update_product, name="update_product"),
    
    path('dashboard/delete_product/', views.delete_product, name='delete_product'),


    # Operation paths
    path('operation/', views.operation, name='operation'),
    path('operation/view/', views.operation, name='operation_view'),
    path('operation/add-to-cart/', views.add_to_cart, name='add_to_cart'),
    path('operation/select-payment/', views.select_payment, name='select_payment'),
    path('operation/complete-transaction/', views.complete_transaction, name='complete_transaction'),

    # Print
    path('operation/print-receipt/', views.print_receipt, name='print_receipt'),
]
