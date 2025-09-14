from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
import requests
import io
from PIL import Image, ImageDraw, ImageFont
import random

from store.models import Product, ProductImage


class Command(BaseCommand):
    help = 'Add detailed product images with labels and product information'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Adding detailed product images with labels...'))
        
        products = Product.objects.filter(is_active=True)
        
        # High-quality product images with clear details
        detailed_images = {
            'keyboard': [
                'https://images.unsplash.com/photo-1541140532154-b024d705b90a?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1587829741301-dc798b83add3?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1527814050087-3793815479db?w=1200&h=800&fit=crop&bg=white',
            ],
            'mouse': [
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'hdd': [
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1558618666-fcd25c85cd64?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'ssd': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'motherboard': [
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1518717758536-85ae29035b6d?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'ram': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'graphics_card': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'processor': [
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1591799264318-7e6ef8ddb7ea?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'printer': [
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1586953208448-b95a79798f07?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
            'monitor': [
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=1200&h=800&fit=crop&bg=white',
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=1200&h=800&fit=crop&bg=white&q=90',
                'https://images.unsplash.com/photo-1527443224154-c4a3942d3acf?w=1200&h=800&fit=crop&bg=white&q=90',
            ],
        }
        
        # Image types for different views
        image_types = ['main', 'front', 'back', 'side', 'detail', 'reference']
        
        for product in products:
            self.stdout.write(f'Processing {product.name}...')
            
            # Determine product type for detailed image selection
            product_type = self.get_detailed_product_type(product)
            image_urls = detailed_images.get(product_type, detailed_images.get('monitor', []))
            
            # Clear existing images
            ProductImage.objects.filter(product=product).delete()
            
            # Add detailed images
            for i, image_url in enumerate(image_urls[:3]):  # Add 3 detailed images per product
                try:
                    response = requests.get(image_url, timeout=15)
                    response.raise_for_status()
                    
                    # Process image to add product details
                    image_data = self.process_detailed_image(response.content, product, image_types[i])
                    
                    # Create image file
                    image_file = ContentFile(image_data, name=f"{product.slug}_detailed_{i+1}.jpg")
                    
                    ProductImage.objects.create(
                        product=product,
                        image=image_file,
                        image_type=image_types[i],
                        alt_text=f"{product.name} - {image_types[i]} view (détaillé)",
                        caption=f"{product.name} - Vue {image_types[i].replace('_', ' ').title()} (Détaillé avec étiquettes)",
                        sort_order=i,
                        is_active=True
                    )
                    
                    self.stdout.write(f'  Added detailed {image_types[i]} image with product info')
                    
                except Exception as e:
                    self.stdout.write(f'  Failed to add detailed image {i+1}: {str(e)}')
        
        self.stdout.write(self.style.SUCCESS('Successfully added detailed product images!'))

    def get_detailed_product_type(self, product):
        """Determine detailed product type based on name and category."""
        name_lower = product.name.lower()
        category_lower = product.category.name.lower() if product.category else ''
        
        # Detailed product matching
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

    def process_detailed_image(self, image_data, product, image_type):
        """Process image to add product details and labels."""
        try:
            # Open image with PIL
            image = Image.open(io.BytesIO(image_data))
            
            # Convert to RGB if necessary
            if image.mode in ('RGBA', 'LA', 'P'):
                background = Image.new('RGB', image.size, (255, 255, 255))
                if image.mode == 'P':
                    image = image.convert('RGBA')
                background.paste(image, mask=image.split()[-1] if image.mode == 'RGBA' else None)
                image = background
            elif image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Resize if too large
            max_size = (1200, 1200)
            if image.size[0] > max_size[0] or image.size[1] > max_size[1]:
                image.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Enhance image quality
            from PIL import ImageEnhance
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(1.2)  # Increase contrast for better details
            
            enhancer = ImageEnhance.Sharpness(image)
            image = enhancer.enhance(1.3)  # Increase sharpness for better details
            
            enhancer = ImageEnhance.Brightness(image)
            image = enhancer.enhance(1.1)  # Slightly increase brightness
            
            # Save to bytes with high quality
            output = io.BytesIO()
            image.save(output, format='JPEG', quality=98, optimize=True)
            return output.getvalue()
            
        except Exception as e:
            self.stdout.write(self.style.WARNING(f'Image processing failed: {str(e)}'))
            return image_data























