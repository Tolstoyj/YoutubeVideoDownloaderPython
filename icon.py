#!/usr/bin/env python3

from PIL import Image, ImageDraw
import os

def create_icon():
    """Create a simple icon for the application."""
    sizes = {
        'ico': [(16, 16), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)],
        'icns': [(16, 16), (32, 32), (64, 64), (128, 128), (256, 256), (512, 512), (1024, 1024)]
    }
    
    def create_base_image(size):
        """Create a base image with the specified size."""
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Background circle
        margin = size // 8
        circle_size = size - (2 * margin)
        draw.ellipse(
            [margin, margin, margin + circle_size, margin + circle_size],
            fill='#009688'  # Material Design Teal
        )
        
        # Play triangle
        triangle_margin = size // 3
        triangle_points = [
            (triangle_margin * 1.2, triangle_margin),
            (size - triangle_margin, size // 2),
            (triangle_margin * 1.2, size - triangle_margin)
        ]
        draw.polygon(triangle_points, fill='white')
        
        return img
    
    # Create Windows ICO
    ico_images = []
    for size in sizes['ico']:
        ico_images.append(create_base_image(size[0]))
    
    ico_path = 'icon.ico'
    ico_images[0].save(ico_path, format='ICO', sizes=sizes['ico'])
    print(f"Created Windows icon: {ico_path}")
    
    # Create macOS ICNS
    if os.system('which iconutil') == 0:  # Check if iconutil is available (macOS)
        iconset_path = 'icon.iconset'
        os.makedirs(iconset_path, exist_ok=True)
        
        for size in sizes['icns']:
            img = create_base_image(size[0])
            icon_size = size[0]
            if icon_size <= 32:
                img.save(f"{iconset_path}/icon_16x16@2x.png" if icon_size == 32 else f"{iconset_path}/icon_16x16.png")
            else:
                img.save(f"{iconset_path}/icon_{icon_size}x{icon_size}.png")
                img.save(f"{iconset_path}/icon_{icon_size//2}x{icon_size//2}@2x.png")
        
        os.system(f"iconutil -c icns {iconset_path}")
        os.system(f"rm -rf {iconset_path}")
        print("Created macOS icon: icon.icns")

if __name__ == '__main__':
    create_icon() 