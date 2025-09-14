"""
Management command to fix empty image files.
"""
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Fix empty image files by removing them and setting fallback images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN MODE - No changes will be made'))
        
        self.stdout.write('Checking for empty image files...')
        
        # Check main images
        products_with_empty_main = []
        for product in Product.objects.all():
            if product.main_image:
                image_path = os.path.join(settings.MEDIA_ROOT, product.main_image.name)
                if os.path.exists(image_path) and os.path.getsize(image_path) == 0:
                    products_with_empty_main.append(product)
        
        self.stdout.write(f'Found {len(products_with_empty_main)} products with empty main images')
        for product in products_with_empty_main:
            self.stdout.write(f'  - Product {product.id}: {product.name}')
        
        # Check gallery images
        gallery_images_empty = []
        for img in ProductImage.objects.all():
            image_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
            if os.path.exists(image_path) and os.path.getsize(image_path) == 0:
                gallery_images_empty.append(img)
        
        self.stdout.write(f'Found {len(gallery_images_empty)} gallery images with empty files')
        for img in gallery_images_empty:
            self.stdout.write(f'  - Product {img.product.id}: {img.image_type} - {img.image.name}')
        
        if not dry_run:
            # Fix main images
            for product in products_with_empty_main:
                self.stdout.write(f'Fixing product {product.id}: {product.name}')
                
                # Remove the empty file
                image_path = os.path.join(settings.MEDIA_ROOT, product.main_image.name)
                try:
                    os.remove(image_path)
                    self.stdout.write(f'  Removed empty file: {product.main_image.name}')
                except OSError as e:
                    self.stdout.write(f'  Error removing file: {e}')
                
                # Clear the main_image field
                product.main_image = None
                product.save()
                self.stdout.write(f'  Cleared main_image field')
            
            # Fix gallery images
            for img in gallery_images_empty:
                self.stdout.write(f'Fixing gallery image for product {img.product.id}: {img.image_type}')
                
                # Remove the empty file
                image_path = os.path.join(settings.MEDIA_ROOT, img.image.name)
                try:
                    os.remove(image_path)
                    self.stdout.write(f'  Removed empty file: {img.image.name}')
                except OSError as e:
                    self.stdout.write(f'  Error removing file: {e}')
                
                # Delete the database record
                img.delete()
                self.stdout.write(f'  Deleted database record')
        
        self.stdout.write(self.style.SUCCESS('Done!'))
        
        if dry_run:
            self.stdout.write(self.style.WARNING('This was a dry run. Use without --dry-run to apply changes.'))
