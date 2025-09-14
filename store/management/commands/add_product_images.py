from django.core.management.base import BaseCommand
from store.models import Product
import os
from django.conf import settings
from django.core.files.base import ContentFile
import io

class Command(BaseCommand):
    help = 'Add placeholder images for all products'

    def handle(self, *args, **options):
        self.stdout.write('🖼️  Adding placeholder images for all products...')
        
        # Create media directory if it doesn't exist
        media_dir = os.path.join(settings.MEDIA_ROOT, 'products')
        os.makedirs(media_dir, exist_ok=True)
        
        products = Product.objects.all()
        updated_count = 0
        
        for product in products:
            try:
                # Generate a placeholder image based on product type
                image = self.generate_product_image(product)
                
                # Save the image
                image_filename = f"{product.slug}.jpg"
                image_path = os.path.join(media_dir, image_filename)
                
                # Convert PIL image to bytes
                img_byte_arr = io.BytesIO()
                image.save(img_byte_arr, format='JPEG', quality=85)
                img_byte_arr.seek(0)
                
                # Save to Django model
                product.main_image.save(
                    image_filename,
                    ContentFile(img_byte_arr.getvalue()),
                    save=True
                )
                
                self.stdout.write(f'✅ Added image for: {product.name}')
                updated_count += 1
                
            except Exception as e:
                self.stdout.write(
                    self.style.WARNING(f'❌ Failed to add image for {product.name}: {str(e)}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'\n🎉 Successfully added images for {updated_count} products!')
        )

    def generate_product_image(self, product):
        """Generate a placeholder image for the product"""
        # Set image dimensions
        width, height = 400, 300
        
        # Create a new image with a gradient background
        image = Image.new('RGB', (width, height), color='white')
        draw = ImageDraw.Draw(image)
        
        # Create gradient background
        for y in range(height):
            # Create a subtle gradient from light blue to white
            color_value = int(240 + (y / height) * 15)
            draw.line([(0, y), (width, y)], fill=(color_value, color_value + 10, 255))
        
        # Add a subtle border
        draw.rectangle([0, 0, width-1, height-1], outline=(200, 200, 200), width=2)
        
        # Add product type icon based on category
        icon_color = self.get_category_color(product.category.name)
        icon_size = 80
        
        # Draw a simple icon based on product type
        icon_x = (width - icon_size) // 2
        icon_y = (height - icon_size) // 2 - 20
        
        if 'monitor' in product.name.lower():
            self.draw_monitor_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'processor' in product.name.lower() or 'cpu' in product.name.lower():
            self.draw_processor_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'ssd' in product.name.lower() or 'hdd' in product.name.lower():
            self.draw_storage_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'graphics' in product.name.lower() or 'gpu' in product.name.lower():
            self.draw_graphics_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'printer' in product.name.lower():
            self.draw_printer_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'keyboard' in product.name.lower():
            self.draw_keyboard_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'mouse' in product.name.lower():
            self.draw_mouse_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'motherboard' in product.name.lower():
            self.draw_motherboard_icon(draw, icon_x, icon_y, icon_size, icon_color)
        elif 'ram' in product.name.lower():
            self.draw_ram_icon(draw, icon_x, icon_y, icon_size, icon_color)
        else:
            self.draw_generic_icon(draw, icon_x, icon_y, icon_size, icon_color)
        
        # Add brand name
        try:
            # Try to use a default font, fallback to basic if not available
            font_size = 16
            font = ImageFont.load_default()
        except:
            font = ImageFont.load_default()
        
        brand_text = product.brand
        text_bbox = draw.textbbox((0, 0), brand_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        text_y = icon_y + icon_size + 10
        
        draw.text((text_x, text_y), brand_text, fill=(50, 50, 50), font=font)
        
        # Add product name (truncated)
        product_name = product.name[:30] + "..." if len(product.name) > 30 else product.name
        text_bbox = draw.textbbox((0, 0), product_name, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        text_y += 20
        
        draw.text((text_x, text_y), product_name, fill=(80, 80, 80), font=font)
        
        # Add price
        price_text = f"{product.price} MAD"
        text_bbox = draw.textbbox((0, 0), price_text, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        text_x = (width - text_width) // 2
        text_y += 20
        
        draw.text((text_x, text_y), price_text, fill=(0, 120, 0), font=font)
        
        return image

    def get_category_color(self, category_name):
        """Get color based on category"""
        colors = {
            'Data Visualization': (70, 130, 180),    # Steel Blue
            'Business Intelligence': (255, 140, 0),   # Dark Orange
            'Data Processing': (50, 205, 50),         # Lime Green
            'Reporting Tools': (220, 20, 60),         # Crimson
            'Predictive Analytics': (138, 43, 226),   # Blue Violet
        }
        return colors.get(category_name, (100, 100, 100))

    def draw_monitor_icon(self, draw, x, y, size, color):
        """Draw a monitor icon"""
        # Monitor frame
        draw.rectangle([x, y, x + size, y + size - 20], outline=color, width=3)
        # Monitor stand
        draw.rectangle([x + size//2 - 10, y + size - 20, x + size//2 + 10, y + size - 5], fill=color)
        # Screen
        draw.rectangle([x + 10, y + 10, x + size - 10, y + size - 30], fill=(240, 240, 240))

    def draw_processor_icon(self, draw, x, y, size, color):
        """Draw a processor icon"""
        # CPU chip
        draw.rectangle([x, y, x + size, y + size], outline=color, width=3, fill=(250, 250, 250))
        # Pins
        for i in range(0, size, 8):
            draw.rectangle([x - 2, y + i, x + 2, y + i + 4], fill=color)
            draw.rectangle([x + size - 2, y + i, x + size + 2, y + i + 4], fill=color)
            draw.rectangle([x + i, y - 2, x + i + 4, y + 2], fill=color)
            draw.rectangle([x + i, y + size - 2, x + i + 4, y + size + 2], fill=color)

    def draw_storage_icon(self, draw, x, y, size, color):
        """Draw a storage device icon"""
        # SSD/HDD shape
        draw.rectangle([x, y + 10, x + size, y + size - 10], outline=color, width=3, fill=(250, 250, 250))
        # Connectors
        draw.rectangle([x - 5, y + size//2 - 5, x + 5, y + size//2 + 5], fill=color)

    def draw_graphics_icon(self, draw, x, y, size, color):
        """Draw a graphics card icon"""
        # GPU card
        draw.rectangle([x, y + 15, x + size, y + size - 15], outline=color, width=3, fill=(250, 250, 250))
        # Fan
        draw.ellipse([x + 10, y + 10, x + 30, y + 30], outline=color, width=2)
        # PCI connector
        draw.rectangle([x - 5, y + size//2 - 8, x + 5, y + size//2 + 8], fill=color)

    def draw_printer_icon(self, draw, x, y, size, color):
        """Draw a printer icon"""
        # Printer body
        draw.rectangle([x + 10, y + 20, x + size - 10, y + size - 10], outline=color, width=3, fill=(250, 250, 250))
        # Paper tray
        draw.rectangle([x + 5, y + size - 10, x + size - 5, y + size - 5], fill=color)

    def draw_keyboard_icon(self, draw, x, y, size, color):
        """Draw a keyboard icon"""
        # Keyboard base
        draw.rectangle([x, y + 20, x + size, y + size - 10], outline=color, width=3, fill=(250, 250, 250))
        # Keys
        for i in range(0, size, 15):
            draw.rectangle([x + i, y + 25, x + i + 10, y + 35], outline=color, width=1)

    def draw_mouse_icon(self, draw, x, y, size, color):
        """Draw a mouse icon"""
        # Mouse body (oval)
        draw.ellipse([x + 10, y + 10, x + size - 10, y + size - 10], outline=color, width=3, fill=(250, 250, 250))
        # Scroll wheel
        draw.rectangle([x + size//2 - 2, y + 15, x + size//2 + 2, y + 25], fill=color)

    def draw_motherboard_icon(self, draw, x, y, size, color):
        """Draw a motherboard icon"""
        # Motherboard outline
        draw.rectangle([x, y, x + size, y + size], outline=color, width=3, fill=(250, 250, 250))
        # Components
        draw.rectangle([x + 10, y + 10, x + 30, y + 30], fill=color)  # CPU socket
        draw.rectangle([x + 40, y + 10, x + 60, y + 20], fill=color)  # RAM slots
        draw.rectangle([x + 70, y + 10, x + 90, y + 20], fill=color)  # RAM slots

    def draw_ram_icon(self, draw, x, y, size, color):
        """Draw a RAM stick icon"""
        # RAM stick
        draw.rectangle([x + 20, y, x + size - 20, y + size], outline=color, width=3, fill=(250, 250, 250))
        # Connector
        draw.rectangle([x + 15, y + size//2 - 5, x + 25, y + size//2 + 5], fill=color)

    def draw_generic_icon(self, draw, x, y, size, color):
        """Draw a generic component icon"""
        # Generic box
        draw.rectangle([x, y, x + size, y + size], outline=color, width=3, fill=(250, 250, 250))
        # Inner details
        draw.rectangle([x + 10, y + 10, x + size - 10, y + size - 10], outline=color, width=1)
