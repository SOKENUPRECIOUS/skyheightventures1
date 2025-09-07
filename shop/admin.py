from django.contrib import admin
from .models import Category, Product, Order, OrderItem
# Register your models here.


admin.site.register(Category)
admin.site.register(Order)
admin.site.register(OrderItem)

admin.site.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'image1', 'slug', 'image1')

