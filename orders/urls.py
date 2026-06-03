from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.CreateRazorpayOrderView.as_view(), name='create_order'),
    path('verify/', views.VerifyPaymentView.as_view(), name='verify_payment'),
    path('user/', views.UserOrdersView.as_view(), name='user_orders'),
    path('admin/list/', views.AdminOrdersView.as_view(), name='admin_orders'),
    path('<int:order_id>/invoice/', views.DownloadInvoiceView.as_view(), name='download_invoice'),
]
