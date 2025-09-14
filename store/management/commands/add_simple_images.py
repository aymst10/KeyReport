from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
import io
from PIL import Image

from store.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Add simple product images'

    def handle(self, *args, **options):
        self.stdout.write('Adding simple product images...')
        
        products = Product.objects.filter(is_active=True)
        
        # Simple image URLs
        image_urls = [
            'https://images.unsplash.com/photo-1496181133206-80ce9b88a853?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
            'https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=800&h=600&fit=crop',
        ]
        
        image_types = ['main', 'front', 'back', 'side', 'detail']
        
        for product in products:
            self.stdout.write(f'Processing {product.name}...')
            
            # Clear existing images
            ProductImage.objects.filter(product=product).delete()
            
            # Add images
            for i, image_url in enumerate(image_urls[:3]):  # Add 3 images per product
                try:
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                    
                    # Create image file
                    image_file = ContentFile(response.content, name=f"{product.slug}_{i+1}.jpg")
                    
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        image_type=image_types[i],
                        alt_text=f"{product.name} - {image_types[i]} view",
                        sort_order=i,
                        is_active=True
                    )
                    
                    self.stdout.write(f'  Added {image_types[i]} image')
                
            except Exception as e:
                    self.stdout.write(f'  Failed to add image {i+1}: {str(e)}')
        
        self.stdout.write('Successfully added product images!')