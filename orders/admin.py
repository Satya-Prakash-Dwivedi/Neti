from django.contrib import admin
from .models import Order

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'quiz', 'amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('user__email', 'user__name', 'quiz__title', 'razorpay_order_id', 'razorpay_payment_id')
    readonly_fields = ('created_at',)
