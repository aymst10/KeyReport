"""
Management command to help assign images to products.
This command will:
1. List all products without images
2. Suggest image sources based on product names
3. Provide a template for bulk image assignment
"""
import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from store.models import Product, ProductImage
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage


class Command(BaseCommand):
    help = 'Help assign images to products without images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--list-only',
            action='store_true',
            help='Only list products without images',
        )
        parser.add_argument(
            '--suggest-sources',
            action='store_true',
            help='Suggest image sources for products',
        )
        parser.add_argument(
            '--download-from-url',
            type=str,
            help='Download image from URL and assign to product ID',
        )
        parser.add_argument(
            '--product-id',
            type=int,
            help='Product ID to assign image to (use with --download-from-url)',
        )

    def handle(self, *args, **options):
        if options['list_only']:
            self.list_products_without_images()
        elif options['suggest_sources']:
            self.suggest_image_sources()
        elif options['download_from_url'] and options['product_id']:
            self.download_and_assign_image(options['download_from_url'], options['product_id'])
        else:
            self.show_help()

    def list_products_without_images(self):
        """List all products that don't have images."""
        self.stdout.write(self.style.SUCCESS('Products without images:'))
        self.stdout.write('=' * 50)
        
        products_without_images = []
        for product in Product.objects.all():
            has_main_image = product.main_image and os.path.exists(
                os.path.join(settings.MEDIA_ROOT, product.main_image.name)
            )
            has_gallery_images = product.images.filter(is_active=True).exists()
            
            if not has_main_image and not has_gallery_images:
                products_without_images.append(product)
        
        if not products_without_images:
            self.stdout.write(self.style.SUCCESS('All products have images! 🎉'))
            return
        
        for product in products_without_images:
            self.stdout.write(f'ID: {product.id} | {product.name} | Category: {product.category.name}')
        
        self.stdout.write(f'\nTotal products without images: {len(products_without_images)}')

    def suggest_image_sources(self):
        """Suggest image sources for products without images."""
        self.stdout.write(self.style.SUCCESS('Image source suggestions:'))
        self.stdout.write('=' * 50)
        
        products_without_images = []
        for product in Product.objects.all():
            has_main_image = product.main_image and os.path.exists(
                os.path.join(settings.MEDIA_ROOT, product.main_image.name)
            )
            has_gallery_images = product.images.filter(is_active=True).exists()
            
            if not has_main_image and not has_gallery_images:
                products_without_images.append(product)
        
        for product in products_without_images:
            self.stdout.write(f'\nProduct: {product.name}')
            self.stdout.write(f'Category: {product.category.name}')
            self.stdout.write(f'Brand: {product.brand or "Unknown"}')
            
            # Generate search suggestions
            search_terms = [
                f"{product.brand} {product.name}" if product.brand else product.name,
                f"{product.category.name} {product.name}",
                f"{product.name} product image",
                f"{product.name} official image"
            ]
            
            self.stdout.write('Suggested search terms:')
            for term in search_terms:
                self.stdout.write(f'  - "{term}"')
            
            self.stdout.write('Suggested sources:')
            self.stdout.write('  - Google Images (https://images.google.com)')
            self.stdout.write('  - Manufacturer website')
            self.stdout.write('  - Amazon product pages')
            self.stdout.write('  - Unsplash (https://unsplash.com) - for generic tech images')
            self.stdout.write('  - Pexels (https://pexels.com) - for generic tech images')
            self.stdout.write('-' * 30)

    def download_and_assign_image(self, image_url, product_id):
        """Download image from URL and assign to product."""
        try:
            product = Product.objects.get(id=product_id)
            self.stdout.write(f'Downloading image for product: {product.name}')
            
            # Download image
            response = requests.get(image_url, timeout=30)
            response.raise_for_status()
            
            # Get file extension
            content_type = response.headers.get('content-type', '')
            if 'jpeg' in content_type or 'jpg' in content_type:
                ext = 'jpg'
            elif 'png' in content_type:
                ext = 'png'
            elif 'webp' in content_type:
                ext = 'webp'
            else:
                ext = 'jpg'  # default
            
            # Create filename
            filename = f"{product.slug}_downloaded.{ext}"
            file_path = f"products/{filename}"
            
            # Save image
            image_file = ContentFile(response.content)
            saved_path = default_storage.save(file_path, image_file)
            
            # Assign to product
            product.main_image = saved_path
            product.save()
            
            self.stdout.write(self.style.SUCCESS(f'✅ Image downloaded and assigned to {product.name}'))
            self.stdout.write(f'Image saved as: {saved_path}')
            
        except Product.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'❌ Product with ID {product_id} not found'))
        except requests.RequestException as e:
            self.stdout.write(self.style.ERROR(f'❌ Error downloading image: {e}'))
                    except Exception as e:
            self.stdout.write(self.style.ERROR(f'❌ Error: {e}'))

    def show_help(self):
        """Show help information."""
        self.stdout.write(self.style.SUCCESS('🖼️  Product Image Assignment Helper'))
        self.stdout.write('=' * 50)
        self.stdout.write('This command helps you assign images to products.')
        self.stdout.write('')
        self.stdout.write('Available options:')
        self.stdout.write('  --list-only          List all products without images')
        self.stdout.write('  --suggest-sources    Suggest image sources for products')
        self.stdout.write('  --download-from-url URL --product-id ID  Download and assign image')
        self.stdout.write('')
        self.stdout.write('Examples:')
        self.stdout.write('  python manage.py assign_product_images --list-only')
        self.stdout.write('  python manage.py assign_product_images --suggest-sources')
        self.stdout.write('  python manage.py assign_product_images --download-from-url "https://example.com/image.jpg" --product-id 76')
        self.stdout.write('')
        self.stdout.write('💡 Tip: Use --suggest-sources to get search terms for finding images!')