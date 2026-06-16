from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
import uuid

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('role', 'ADMIN')
        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = (
        ('STUDENT', 'Student'),
        ('EDUCATOR', 'Educator'),
        ('ADMIN', 'Admin'),
    )

    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='STUDENT')
    purchased_products = models.JSONField(default=list, blank=True)  # List of product IDs purchased
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    referral_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    referral_points = models.IntegerField(default=0)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def save(self, *args, **kwargs):
        import random
        if not self.referral_code:
            first_name = self.name.split()[0].upper() if self.name else "USER"
            first_name = ''.join(e for e in first_name if e.isalnum())
            base_code = first_name[:6]
            
            while True:
                random_num = str(random.randint(1000, 9999))
                code = f"{base_code}{random_num}"
                if not CustomUser.objects.filter(referral_code=code).exists():
                    self.referral_code = code
                    break
        super().save(*args, **kwargs)

    def __str__(self):
        return self.email
