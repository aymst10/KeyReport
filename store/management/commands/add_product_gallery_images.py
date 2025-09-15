from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
import os
import requests
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import uuid


class Command(BaseCommand):
    help = 'Add additional product images to products that only have main images'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be added without making changes',
        )
        parser.add_argument(
            '--limit',
            type=int,
            default=5,
            help='Maximum number of additional images to add per product',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        limit = options['limit']
        
        self.stdout.write('🖼️  Adding additional product images...')
        self.stdout.write('=' * 60)
        
        # Find products that only have main images but no additional product images
        products_needing_images = []
        
        for product in Product.objects.filter(is_active=True):
            # Check if product has a main image
            has_main_image = False
            if product.main_image:
                try:
                    has_main_image = os.path.exists(product.main_image.path) and os.path.getsize(product.main_image.path) > 0
                except:
                    has_main_image = False
            
            # Check product images count
            product_images_count = product.images.count()
            
            # If product only has main image but no additional product images
            if has_main_image and product_images_count == 0:
                products_needing_images.append(product)
        
        if not products_needing_images:
            self.stdout.write(self.style.SUCCESS('All products already have additional images! 🎉'))
            return
        
        self.stdout.write(f'Found {len(products_needing_images)} products needing additional images:')
        
        # Image sources for different product types
        image_sources = {
            'monitor': [
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1593640408182-31c70c8268f5?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1587831990711-23ca6441447b?w=800&h=600&fit=crop',
            ],
            'headset': [
                'https://images.unsplash.com/photo-1572536147248-ac59a8abfa4b?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1599669454699-248893623440?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=800&h=600&fit=crop',
            ],
            'gaming': [
                'https://images.unsplash.com/photo-1493711662062-fa541adb3fc8?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1511512578047-dfb367046420?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1606144042614-b2417e99c4e3?w=800&h=600&fit=crop',
            ],
            'default': [
                'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1556742049-0cfed4f6a45d?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1556742111-a301076d9d18?w=800&h=600&fit=crop',
            ]
        }
        
        for product in products_needing_images:
            self.stdout.write(f'\\n📦 Processing: {product.name}')
            
            # Determine image category based on product name and category
            image_category = 'default'
            product_name_lower = product.name.lower()
            category_name_lower = product.category.name.lower() if product.category else ''
            
            if 'monitor' in product_name_lower or 'monitor' in category_name_lower:
                image_category = 'monitor'
            elif 'headset' in product_name_lower or 'gaming' in product_name_lower:
                image_category = 'headset'
            elif 'gaming' in product_name_lower or 'gaming' in category_name_lower:
                image_category = 'gaming'
            
            # Get images for this category
            images_to_add = image_sources.get(image_category, image_sources['default'])[:limit]
            
            if dry_run:
                self.stdout.write(f'  Would add {len(images_to_add)} images from category: {image_category}')
                for i, img_url in enumerate(images_to_add, 1):
                    self.stdout.write(f'    {i}. {img_url}')
            else:
                self.stdout.write(f'  Adding {len(images_to_add)} images from category: {image_category}')
                
                for i, img_url in enumerate(images_to_add, 1):
                    try:
                        # Download image
                        response = requests.get(img_url, timeout=10)
                        response.raise_for_status()
                        
                        # Generate unique filename
                        file_extension = img_url.split('.')[-1].split('?')[0]
                        if file_extension not in ['jpg', 'jpeg', 'png', 'webp']:
                            file_extension = 'jpg'
                        
                        filename = f"{product.slug}_gallery_{i}_{uuid.uuid4().hex[:8]}.{file_extension}"
                        
                        # Save image
                        image_file = ContentFile(response.content)
                        
                        # Create ProductImage instance
                        product_image = ProductImage.objects.create(
                            product=product,
                            image=image_file,
                            alt_text=f"{product.name} - Gallery Image {i}",
                            image_type='detail',
                            caption=f"Additional view of {product.name}"
                        )
                        
                        # Save the file
                        product_image.image.save(filename, image_file, save=True)
                        
                        self.stdout.write(f'    ✅ Added image {i}: {filename}')
                        
                    except Exception as e:
                        self.stdout.write(f'    ❌ Failed to add image {i}: {str(e)}')
        
        if not dry_run:
            self.stdout.write(f'\\n🎉 Successfully processed {len(products_needing_images)} products!')
            self.stdout.write('Additional product images have been added to enhance the product catalog.')
        else:
            self.stdout.write(f'\\n📋 Dry run completed. {len(products_needing_images)} products would be processed.')
            self.stdout.write('Run without --dry-run to actually add the images.')
