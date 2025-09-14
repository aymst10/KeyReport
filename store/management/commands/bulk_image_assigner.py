"""
Bulk image assignment tool with predefined image URLs for common products.
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, ProductImage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Bulk assign images to products using predefined image sources'

    def add_arguments(self, parser):
        parser.add_argument(
            '--auto-assign',
            action='store_true',
            help='Automatically assign images based on product names',
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be assigned without making changes',
        )

    def handle(self, *args, **options):
        if options['auto_assign']:
            self.auto_assign_images(options['dry_run'])
        else:
            self.show_help()

    def auto_assign_images(self, dry_run=False):
        """Automatically assign images based on product names."""
        
        # Predefined image URLs for common products
        image_sources = {
            # Gaming Headsets
            'hyperx': 'https://images.unsplash.com/photo-1599669454699-248893623440?w=500&h=500&fit=crop',
            'headset': 'https://images.unsplash.com/photo-1599669454699-248893623440?w=500&h=500&fit=crop',
            'gaming headset': 'https://images.unsplash.com/photo-1599669454699-248893623440?w=500&h=500&fit=crop',
            
            # Monitors
            'dell': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&h=500&fit=crop',
            'monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&h=500&fit=crop',
            'business monitor': 'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=500&h=500&fit=crop',
            
            # Keyboards
            'keyboard': 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500&h=500&fit=crop',
            'mechanical keyboard': 'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=500&h=500&fit=crop',
            
            # Mice
            'mouse': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&h=500&fit=crop',
            'gaming mouse': 'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=500&h=500&fit=crop',
            
            # Printers
            'printer': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=500&h=500&fit=crop',
            'canon': 'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=500&h=500&fit=crop',
            
            # Storage
            'ssd': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500&h=500&fit=crop',
            'hard drive': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500&h=500&fit=crop',
            
            # Graphics Cards
            'graphics': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500&h=500&fit=crop',
            'gpu': 'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=500&h=500&fit=crop',
            
            # Default tech image
            'default': 'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=500&h=500&fit=crop'
        }
        
        self.stdout.write(self.style.SUCCESS('🖼️  Auto-assigning images to products...'))
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('=' * 60)
        
        # Get products without images
        products_without_images = []
        for product in Product.objects.all():
            has_main_image = product.main_image and os.path.exists(
                os.path.join(settings.MEDIA_ROOT, product.main_image.name)
            )
            has_gallery_images = product.images.filter(is_active=True).exists()
            
            if not has_main_image and not has_gallery_images:
                products_without_images.append(product)
        
        if not products_without_images:
            self.stdout.write(self.style.SUCCESS('All products already have images! 🎉'))
            return
        
        assigned_count = 0
        
        for product in products_without_images:
            # Find matching image source
            product_name_lower = product.name.lower()
            image_url = None
            
            for keyword, url in image_sources.items():
                if keyword in product_name_lower:
                    image_url = url
                    break
            
            if not image_url:
                image_url = image_sources['default']
            
            self.stdout.write(f'Product: {product.name}')
            self.stdout.write(f'Image URL: {image_url}')
            
            if not dry_run:
                try:
                    # Download image
                    response = requests.get(image_url, timeout=30)
                    response.raise_for_status()
                    
                    # Create filename
                    filename = f"{product.slug}_auto_assigned.jpg"
                    file_path = f"products/{filename}"
                    
                    # Save image
                    image_file = ContentFile(response.content)
                    saved_path = default_storage.save(file_path, image_file)
                    
                    # Assign to product
                    product.main_image = saved_path
                    product.save()
                    
                    self.stdout.write(self.style.SUCCESS(f'✅ Image assigned successfully'))
                    assigned_count += 1
                    
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))
            else:
                self.stdout.write(self.style.WARNING('Would assign image (dry run)'))
                assigned_count += 1
            
            self.stdout.write('-' * 40)
        
        if dry_run:
            self.stdout.write(self.style.SUCCESS(f'Would assign images to {assigned_count} products'))
            self.stdout.write(self.style.WARNING('Run without --dry-run to apply changes'))
        else:
            self.stdout.write(self.style.SUCCESS(f'✅ Successfully assigned images to {assigned_count} products!'))

    def show_help(self):
        """Show help information."""
        self.stdout.write(self.style.SUCCESS('🖼️  Bulk Image Assignment Tool'))
        self.stdout.write('=' * 50)
        self.stdout.write('This tool automatically assigns images to products based on their names.')
        self.stdout.write('')
        self.stdout.write('Available options:')
        self.stdout.write('  --auto-assign    Automatically assign images to products')
        self.stdout.write('  --dry-run        Show what would be assigned without making changes')
        self.stdout.write('')
        self.stdout.write('Examples:')
        self.stdout.write('  python manage.py bulk_image_assigner --auto-assign --dry-run')
        self.stdout.write('  python manage.py bulk_image_assigner --auto-assign')
        self.stdout.write('')
        self.stdout.write('💡 The tool uses Unsplash images and matches products by keywords!')
