from django.db import models
from django.conf import settings
from quizzes.models import Quiz, Book

class Order(models.Model):
    STATUS_CHOICES = (
        ('Pending', 'Pending'),
        ('Paid', 'Paid'),
        ('Failed', 'Failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='orders', on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    book = models.ForeignKey(Book, related_name='orders', on_delete=models.CASCADE, null=True, blank=True)
    razorpay_order_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=255, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)
    referral_code_used = models.CharField(max_length=10, null=True, blank=True)
    discount_applied = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        pass

    def __str__(self):
        return f"Order {self.id} by {self.user.email} - {self.status}"
