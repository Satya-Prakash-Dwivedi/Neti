from django.db import models

class Product(models.Model):
    """Represents a paid Question Bank PDF product."""
    title = models.CharField(max_length=255)
    description = models.TextField()
    subject = models.CharField(max_length=100)  # e.g., Polity, History
    chapter = models.CharField(max_length=100)  # e.g., Fundamental Rights
    price = models.DecimalField(max_digits=10, decimal_places=2)  # Secure money field
    
    # Store PDFs and thumbnails in subfolders
    # Using FileField for thumbnails to avoid requiring the 'Pillow' image library.
    pdf_file = models.FileField(upload_to='pdfs/')
    thumbnail = models.FileField(upload_to='thumbnails/', blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.subject} - {self.chapter}: {self.title}"