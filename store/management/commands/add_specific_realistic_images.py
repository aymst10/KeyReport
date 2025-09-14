from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
import io
from PIL import Image
import random

from store.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Add specific realistic images for each component type'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding specific realistic product images...'))
        
        products = Product.objects.filter(is_active=True)
        
        # Very specific realistic image URLs for each product type
        specific_images = {
            'keyboard': [
                'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1527814050087-3793815479db?w=800&h=600&fit=crop',
            ],
            'mouse': [
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=800&h=600&fit=crop&q=80',
            ],
            'hdd': [
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=800&h=600&fit=crop&q=80',
            ],
            'ssd': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
            ],
            'motherboard': [
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=800&h=600&fit=crop&q=80',
            ],
            'ram': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
            ],
            'graphics_card': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
            ],
            'processor': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=800&h=600&fit=crop&q=80',
            ],
            'printer': [
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=800&h=600&fit=crop&q=80',
            ],
            'monitor': [
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop',
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop&q=80',
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=800&h=600&fit=crop&q=80',
            ],
        }
        
        # Image types for different views
        image_types = ['main', 'front', 'back', 'side', 'detail', 'reference']
        
        for product in products:
            self.stdout.write(f'Processing {product.name}...')
            
            # Determine product type for specific image selection
            product_type = self.get_specific_product_type(product)
            image_urls = specific_images.get(product_type, specific_images.get('monitor', []))
            
            # Clear existing images
            ProductImage.objects.filter(product=product).delete()
            
            # Add specific realistic images
            for i, image_url in enumerate(image_urls[:3]):  # Add 3 specific images per product
                try:
                    response = requests.get(image_url, timeout=10)
                    response.raise_for_status()
                    
                    # Create image file
                    image_file = ContentFile(response.content, name=f"{product.slug}_specific_{i+1}.jpg")
                    
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        image_type=image_types[i],
                        alt_text=f"{product.name} - {image_types[i]} view (spécifique)",
                        caption=f"{product.name} - Vue {image_types[i].replace('_', ' ').title()} (Spécifique)",
                        sort_order=i,
                        is_active=True
                    )
                    
                    self.stdout.write(f'  Added specific {image_types[i]} image')
                    
                except Exception as e:
                    self.stdout.write(f'  Failed to add specific image {i+1}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added specific realistic product images!'))

    def get_specific_product_type(self, product):
        """Determine specific product type based on name and category."""
        name_lower = product.name.lower()
        category_lower = product.category.name.lower() if product.category else ''
        
        # Very specific product matching
        if any(word in name_lower for word in ['keyboard', 'clavier', 'surface']):
            return 'keyboard'
        elif any(word in name_lower for word in ['mouse', 'souris', 'mx master']):
            return 'mouse'
        elif any(word in name_lower for word in ['hdd', 'hard drive', 'disque dur', 'barracuda']):
            return 'hdd'
        elif any(word in name_lower for word in ['ssd', 'nvme', 'solid state', 'sn850', '980 pro']):
            return 'ssd'
        elif any(word in name_lower for word in ['motherboard', 'carte mère', 'mainboard', 'b550', 'tomahawk']):
            return 'motherboard'
        elif any(word in name_lower for word in ['ram', 'memory', 'mémoire', 'vengeance', 'lpx']):
            return 'ram'
        elif any(word in name_lower for word in ['graphics', 'gpu', 'carte graphique', 'radeon', 'geforce', 'rtx', 'rx']):
            return 'graphics_card'
        elif any(word in name_lower for word in ['processor', 'cpu', 'ryzen', 'intel', 'core', '5900x', '12700k']):
            return 'processor'
        elif any(word in name_lower for word in ['printer', 'imprimante', 'pixma', 'laserjet', 'g6020', 'm404dn']):
            return 'printer'
        elif any(word in name_lower for word in ['monitor', 'écran', 'screen', 'display', 'dell', 'lg', 'samsung', 'ultrawide']):
            return 'monitor'
        else:
            return 'monitor'  # Default to monitor























