from rest_framework import generics, permissions
from .models import Product
from .serializers import ProductSerializer

class ProductListView(generics.ListAPIView):
    """Public endpoint to list all available Question Bank PDFs."""
    queryset = Product.objects.all().order_by('-created_at')
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)  # Open to everyone

class ProductDetailView(generics.RetrieveAPIView):
    """Public endpoint to view detail of a single Question Bank PDF."""
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (permissions.AllowAny,)  # Open to everyone