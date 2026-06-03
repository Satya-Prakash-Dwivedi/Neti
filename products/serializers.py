from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    """Serializes Product instances, dynamically hiding PDF links from non-purchasers."""
    pdf_file = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = ('id', 'title', 'description', 'subject', 'chapter', 'price', 'thumbnail', 'pdf_file', 'created_at')

    def get_pdf_file(self, obj):
        request = self.context.get('request')
        # Check if user is authenticated
        if request and request.user and request.user.is_authenticated:
            user = request.user
            # Check if user is educator/admin, or has purchased the product
            # (Checking if the product ID is inside the user's purchased_products JSON array)
            if user.role in ['ADMIN', 'EDUCATOR'] or obj.id in user.purchased_products:
                # Return the absolute download URL
                return request.build_absolute_uri(obj.pdf_file.url) if obj.pdf_file else None
        
        # Hide PDF URL for unauthorized users
        return None