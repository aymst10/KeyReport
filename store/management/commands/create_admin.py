from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a superuser for admin access'

    def handle(self, *args, **options):
        self.stdout.write('🔐 Creating admin superuser...')
        
        # Check if admin user already exists
        if User.objects.filter(email='admin@keyreport.com').exists():
            self.stdout.write(self.style.WARNING('Admin user already exists!'))
            return
        
        # Create superuser
        admin_user = User.objects.create_superuser(
            email='admin@keyreport.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ Admin user created successfully!')
        )
        self.stdout.write(f'📧 Email: admin@keyreport.com')
        self.stdout.write(f'🔑 Password: admin123')
        self.stdout.write(f'🌐 Admin URL: http://127.0.0.1:8000/admin/')
        self.stdout.write(f'📊 Store Dashboard: http://127.0.0.1:8000/store/admin/dashboard/')







