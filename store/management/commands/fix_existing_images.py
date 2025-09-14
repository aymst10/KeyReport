from django.core.management.base import BaseCommand
from store.models import Product, ProductImage
from django.core.files import File
import os
from pathlib import Path
import shutil

class Command(BaseCommand):
    help = 'Fix existing images by ensuring they are properly linked'

    def handle(self, *args, **options):
        media_dir = Path('media/products')
        updated_count = 0
        
        for product in Product.objects.all():
            product_name_lower = product.name.lower()
            
            # Check if product has an image
            if product.main_image and product.main_image.name:
                # Check if the image file actually exists
                image_path = media_dir / product.main_image.name
                if image_path.exists():
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ {product.name} already has a working image: {product.main_image.name}'
                        )
                    )
                    continue
            
            # Try to find a matching image file in the media directory
            matching_image = None
            for img_file in media_dir.iterdir():
                if img_file.is_file() and img_file.suffix.lower() in ['.jpg', '.jpeg', '.png']:
                    img_name_lower = img_file.name.lower()
                    
                    # Check if the image name contains product keywords
                    product_keywords = []
                    for word in product_name_lower.split():
                        if len(word) > 3:  # Only use meaningful words
                            product_keywords.append(word)
                    
                    # Check for matches
                    if any(keyword in img_name_lower for keyword in product_keywords):
                        matching_image = img_file
                        break
            
            if matching_image:
                try:
                    # Copy the image to create a new file for this product
                    new_filename = f"{product.slug}-fixed.jpg"
                    new_path = media_dir / new_filename
                    
                    # Copy the file
                    shutil.copy2(matching_image, new_path)
                    
                    # Update the product's main image
                    with open(new_path, 'rb') as f:
                        django_file = File(f)
                        product.main_image.save(
                            new_filename,
                            django_file,
                            save=True
                        )
                    
                    # Clear existing gallery images and create new ones
                    product.images.all().delete()
                    
                    # Create ProductImage entry
                    ProductImage.objects.create(
                        product=product,
                        image=product.main_image,
                        image_type='main',
                        alt_text=f"{product.name} - Product Image",
                        caption=f"Image du produit {product.name}",
                        sort_order=1,
                        is_active=True
                    )
                    
                    updated_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(
                            f'✓ Fixed image for {product.name} using {matching_image.name}'
                        )
                    )
                    
                except Exception as e:
                    self.stdout.write(
                        self.style.ERROR(
                            f'✗ Error fixing image for {product.name}: {e}'
                        )
                    )
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f'⚠ No matching image found for: {product.name}'
                    )
                )
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully fixed images for {updated_count} products'
            )
        )
        
        # Show summary
        total_products = Product.objects.count()
        products_with_images = Product.objects.exclude(main_image='').count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Summary: {products_with_images}/{total_products} products now have images ({(products_with_images/total_products)*100:.1f}%)'
            )
        )

