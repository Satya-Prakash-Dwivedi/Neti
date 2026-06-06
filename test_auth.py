import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from django.contrib.auth import authenticate
user = authenticate(email='satya@admin.com', password='admin')
print("Authenticated user:", user)
if user is None:
    from authentication.models import CustomUser
    u = CustomUser.objects.get(email='satya@admin.com')
    print("Direct check:", u.check_password('admin'))
