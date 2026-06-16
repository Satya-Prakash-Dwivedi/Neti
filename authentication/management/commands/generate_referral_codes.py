import uuid
from django.core.management.base import BaseCommand
from authentication.models import CustomUser

class Command(BaseCommand):
    help = 'Generates referral codes for existing users who do not have one.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Print what would happen without actually saving to the database.',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        # Find users without a code
        users_without_code = CustomUser.objects.filter(referral_code__isnull=True)
        count = users_without_code.count()
        
        if count == 0:
            self.stdout.write(self.style.SUCCESS('All users already have a referral code.'))
            return

        self.stdout.write(f'Found {count} users without a referral code.')

        if dry_run:
            self.stdout.write(self.style.WARNING('[DRY RUN] No changes will be made to the database.'))
            for user in users_without_code:
                self.stdout.write(f'Would generate code for: {user.email}')
            return

        # Actual Update
        updated_count = 0
        for user in users_without_code:
            # Collision retry loop
            import random
            first_name = user.name.split()[0].upper() if user.name else "USER"
            first_name = ''.join(e for e in first_name if e.isalnum())
            base_code = first_name[:6]
            
            while True:
                random_num = str(random.randint(1000, 9999))
                code = f"{base_code}{random_num}"
                if not CustomUser.objects.filter(referral_code=code).exists():
                    user.referral_code = code
                    break
            
            # Save ONLY the referral_code field
            user.save(update_fields=['referral_code'])
            updated_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully generated codes for {updated_count} users.'))
