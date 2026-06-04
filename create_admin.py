import os
import sys
import django
import argparse

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

from authentication.models import CustomUser

def create_admin(email, name, password):
    if CustomUser.objects.filter(email=email).exists():
        print(f"Error: User with email '{email}' already exists.")
        
        # Optionally, upgrade existing user to admin
        user = CustomUser.objects.get(email=email)
        if user.role != 'ADMIN':
            user.role = 'ADMIN'
            user.is_staff = True
            user.is_superuser = True
            user.save()
            print(f"Upgraded existing user '{email}' to ADMIN.")
        return

    try:
        user = CustomUser.objects.create_superuser(
            email=email,
            name=name,
            password=password
        )
        print(f"Success: Admin user '{email}' created successfully!")
    except Exception as e:
        print(f"Failed to create admin: {e}")

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Create an admin user.')
    parser.add_argument('--email', required=True, help='Admin email address')
    parser.add_argument('--name', required=True, help='Admin full name')
    parser.add_argument('--password', required=True, help='Admin password')
    
    args = parser.parse_args()
    create_admin(args.email, args.name, args.password)
