from django.contrib import admin
from .models import Product

class ProductAdmin(admin.ModelAdmin):
    list_display = ('title', 'subject', 'chapter', 'price', 'created_at')
    list_filter = ('subject', 'created_at')
    search_fields = ('title', 'subject', 'chapter')

admin.site.register(Product, ProductAdmin)