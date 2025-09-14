from PIL import Image, ImageDraw, ImageFont
import os
from pathlib import Path

def create_sample_product_photo(product_name, filename):
    """Create a sample product photo with text overlay"""
    # Create a white background image
    img = Image.new('RGB', (800, 600), color='white')
    draw = ImageDraw.Draw(img)
    
    # Try to use a default font, fallback to basic if not available
    try:
        font_large = ImageFont.truetype("arial.ttf", 48)
        font_medium = ImageFont.truetype("arial.ttf", 24)
    except:
        font_large = ImageFont.load_default()
        font_medium = ImageFont.load_default()
    
    # Add product name
    text_lines = product_name.split(' ')
    y_position = 200
    
    for line in text_lines:
        # Get text dimensions
        bbox = draw.textbbox((0, 0), line, font=font_large)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        # Center the text
        x_position = (800 - text_width) // 2
        draw.text((x_position, y_position), line, fill='black', font=font_large)
        y_position += text_height + 10
    
    # Add "Professional Product Photo" text
    draw.text((250, 400), "Professional Product Photo", fill='gray', font=font_medium)
    
    # Save the image
    photo_dir = Path('user_photos')
    photo_dir.mkdir(exist_ok=True)
    img.save(photo_dir / filename)
    print(f"Created sample photo: {filename}")

# Create sample photos for the products we have
sample_photos = [
    ("Seagate Barracuda 4TB HDD", "seagate-barracuda-4tb.jpg"),
    ("Corsair Vengeance LPX RAM", "corsair-vengeance-ram.jpg"),
    ("Logitech MX Master 3S Mouse", "logitech-mx-master-mouse.jpg"),
    ("MSI MAG B550 Tomahawk Motherboard", "msi-tomahawk-motherboard.jpg"),
    ("ASUS ROG Strix B550-F Motherboard", "asus-rog-strix-motherboard.jpg"),
    ("Microsoft Surface Keyboard", "surface-keyboard.jpg"),
    ("NVIDIA GeForce RTX 4070 Graphics Card", "nvidia-rtx-4070-graphics.jpg"),
    ("AMD Radeon RX 7800 XT Graphics Card", "amd-rx-7800-graphics.jpg"),
    ("Samsung 980 PRO SSD", "samsung-980-pro-ssd.jpg"),
    ("Intel Core i7-12700K Processor", "intel-i7-12700k-processor.jpg"),
]

if __name__ == "__main__":
    try:
        from PIL import Image, ImageDraw, ImageFont
        print("Creating sample product photos...")
        
        for product_name, filename in sample_photos:
            create_sample_product_photo(product_name, filename)
        
        print("Sample photos created successfully!")
        
    except ImportError:
        print("PIL (Pillow) not installed. Creating placeholder files instead...")
        
        # Create placeholder text files if PIL is not available
        photo_dir = Path('user_photos')
        photo_dir.mkdir(exist_ok=True)
        
        for product_name, filename in sample_photos:
            placeholder_file = photo_dir / filename.replace('.jpg', '.txt')
            with open(placeholder_file, 'w') as f:
                f.write(f"Placeholder for {product_name}\n")
                f.write("Replace this file with the actual product photo\n")
            print(f"Created placeholder: {placeholder_file}")
        
        print("Placeholder files created. Please replace them with actual photos.")

