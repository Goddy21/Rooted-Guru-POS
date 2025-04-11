from django.contrib import admin
from .models import Product, Profile

class ProductAdmin(admin.ModelAdmin):
    list_display = ('product_code', 'name', 'price', 'stock_level', 'sales_count', 'order_received', 'last_purchase', 'ordered')
    search_fields = ('name', 'product_code')
    
admin.site.register(Product, ProductAdmin)
admin.site.register(Profile)
