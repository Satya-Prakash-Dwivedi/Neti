import os, django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "core.settings")
django.setup()
from authentication.models import CustomUser
u = CustomUser.objects.get(email='satya@admin.com')
print("Active:", u.is_active)
print("Password check 'admin':", u.check_password('admin'))
print("Password check '\"admin\"':", u.check_password('"admin"'))
