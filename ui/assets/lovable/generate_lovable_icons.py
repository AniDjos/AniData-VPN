#!/usr/bin/env python3
"""
Generate lovable.ai style icons for the AniData VPN application
with enhanced elegance and modern aesthetics
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import math
from PIL.ImageDraw import floodfill

# Colors in the lovable.ai style - enhanced for elegance
COLORS = {
    'primary': '#6c5ce7',
    'primary_gradient_end': '#8075e5',
    'secondary': '#0abde3',
    'secondary_gradient_end': '#36c7e8',
    'danger': '#ff7979',
    'danger_gradient_end': '#ff9191',
    'success': '#38b2ac',
    'success_gradient_end': '#4ccbc5',
    'warning': '#f7b731',
    'warning_gradient_end': '#ffc754',
    'background': '#f7f9fc',
    'dark_background': '#2d3436',
    'text': '#4a4a4a',
    'white': '#ffffff',
    'light_shadow': '#f0f4f9',
}

# Directory to save icons
SAVE_DIR = os.path.dirname(os.path.abspath(__file__))

def hex_to_rgb(hex_color):
    """Convert hex color to RGB tuple"""
    hex_color = hex_color.lstrip('#')
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def hex_to_rgba(hex_color, alpha=255):
    """Convert hex color to RGBA tuple"""
    rgb = hex_to_rgb(hex_color)
    return rgb + (alpha,)

def create_gradient(width, height, color1, color2, direction='horizontal'):
    """Create a gradient image between two colors"""
    base = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(base)
    
    r1, g1, b1 = hex_to_rgb(color1)
    r2, g2, b2 = hex_to_rgb(color2)
    
    if direction == 'horizontal':
        for x in range(width):
            # Calculate gradient color at this position
            r = int(r1 + (r2 - r1) * x / width)
            g = int(g1 + (g2 - g1) * x / width)
            b = int(b1 + (b2 - b1) * x / width)
            draw.line([(x, 0), (x, height)], fill=(r, g, b, 255))
    else:  # vertical
        for y in range(height):
            # Calculate gradient color at this position
            r = int(r1 + (r2 - r1) * y / height)
            g = int(g1 + (g2 - g1) * y / height)
            b = int(b1 + (b2 - b1) * y / height)
            draw.line([(0, y), (width, y)], fill=(r, g, b, 255))
            
    return base

def create_rounded_rectangle(draw, xy, radius, fill=None, outline=None, width=0, gradient=None):
    """Draw a rounded rectangle with optional gradient fill"""
    x1, y1, x2, y2 = xy
    
    # If we have a gradient, create a mask for it
    if gradient:
        # Create a mask with the rounded rectangle shape
        mask = Image.new('L', (x2-x1, y2-y1), 0)
        mask_draw = ImageDraw.Draw(mask)
        
        # Draw the rounded rectangle on the mask
        mask_draw.rectangle((radius, 0, x2-x1-radius, y2-y1), fill=255)
        mask_draw.rectangle((0, radius, x2-x1, y2-y1-radius), fill=255)
        mask_draw.pieslice((0, 0, 2*radius, 2*radius), 180, 270, fill=255)
        mask_draw.pieslice((x2-x1-2*radius, 0, x2-x1, 2*radius), 270, 0, fill=255)
        mask_draw.pieslice((0, y2-y1-2*radius, 2*radius, y2-y1), 90, 180, fill=255)
        mask_draw.pieslice((x2-x1-2*radius, y2-y1-2*radius, x2-x1, y2-y1), 0, 90, fill=255)
        
        # Apply the mask to the gradient
        gradient = gradient.resize((x2-x1, y2-y1))
        gradient.putalpha(mask)
        
        # Paste the masked gradient onto the image at the right position
        draw._image.paste(gradient, (x1, y1), gradient)
    else:
        # Standard drawing with solid color
        draw.rectangle((x1 + radius, y1, x2 - radius, y2), fill=fill, outline=outline, width=width)
        draw.rectangle((x1, y1 + radius, x2, y2 - radius), fill=fill, outline=outline, width=width)
        draw.pieslice((x1, y1, x1 + 2 * radius, y1 + 2 * radius), 180, 270, fill=fill, outline=outline, width=width)
        draw.pieslice((x2 - 2 * radius, y1, x2, y1 + 2 * radius), 270, 0, fill=fill, outline=outline, width=width)
        draw.pieslice((x1, y2 - 2 * radius, x1 + 2 * radius, y2), 90, 180, fill=fill, outline=outline, width=width)
        draw.pieslice((x2 - 2 * radius, y2 - 2 * radius, x2, y2), 0, 90, fill=fill, outline=outline, width=width)

def add_soft_shadow(img, blur_radius=10, opacity=100, offset=(0, 4)):
    """Add a soft shadow to an image"""
    # Create a shadow image with transparent background
    shadow = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # Create a mask from the original image's alpha channel
    mask = img.split()[3]
    
    # Draw the shadow using the mask
    shadow_draw = ImageDraw.Draw(shadow)
    shadow_draw.bitmap((0, 0), mask, fill=(0, 0, 0, opacity))
    
    # Blur the shadow
    shadow = shadow.filter(ImageFilter.GaussianBlur(blur_radius))
    
    # Create a new image with transparent background
    result = Image.new('RGBA', img.size, (0, 0, 0, 0))
    
    # Paste the shadow with offset
    result.paste(shadow, offset, shadow)
    
    # Paste the original image on top
    result.paste(img, (0, 0), img)
    
    return result

def create_connect_icon(size=64, bg_color=COLORS['secondary'], bg_gradient=COLORS['secondary_gradient_end'], fg_color=COLORS['white']):
    """Create an elegant connect icon in lovable.ai style"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient for background
    padding = size // 8
    circle_size = size - 2 * padding
    gradient = create_gradient(circle_size, circle_size, bg_color, bg_gradient)
    
    # Create circle mask
    mask = Image.new('L', (circle_size, circle_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, circle_size, circle_size), fill=255)
    
    # Apply mask to gradient
    circle_img = gradient.copy()
    circle_img.putalpha(mask)
    
    # Paste the circle
    img.paste(circle_img, (padding, padding), circle_img)
    
    # Draw the play triangle with a soft glow effect
    triangle_padding = size // 3
    points = [
        (triangle_padding + size // 6, size // 3),
        (triangle_padding + size // 6, 2 * size // 3),
        (2 * size // 3, size // 2)
    ]
    
    # Draw the triangle with anti-aliasing
    draw.polygon(points, fill=fg_color)
    
    # Add a subtle shadow
    img = add_soft_shadow(img, blur_radius=8, opacity=80)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'connect.png'))
    return img

def create_disconnect_icon(size=64, bg_color=COLORS['danger'], bg_gradient=COLORS['danger_gradient_end'], fg_color=COLORS['white']):
    """Create an elegant disconnect icon in lovable.ai style"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient for background
    padding = size // 8
    circle_size = size - 2 * padding
    gradient = create_gradient(circle_size, circle_size, bg_color, bg_gradient)
    
    # Create circle mask
    mask = Image.new('L', (circle_size, circle_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, circle_size, circle_size), fill=255)
    
    # Apply mask to gradient
    circle_img = gradient.copy()
    circle_img.putalpha(mask)
    
    # Paste the circle
    img.paste(circle_img, (padding, padding), circle_img)
    
    # Draw a rounded stop square
    square_padding = size // 3
    square_size = size - 2 * square_padding
    rounded_rect_radius = square_size // 5
    
    # Create a mask for the rounded rectangle
    square_mask = Image.new('L', (square_size, square_size), 0)
    square_mask_draw = ImageDraw.Draw(square_mask)
    create_rounded_rectangle(square_mask_draw, 
                            (0, 0, square_size, square_size), 
                            rounded_rect_radius, 
                            fill=255)
    
    # Create a white square with the mask
    square_img = Image.new('RGBA', (square_size, square_size), fg_color)
    square_img.putalpha(square_mask)
    
    # Paste the rounded square
    img.paste(square_img, (square_padding, square_padding), square_img)
    
    # Add a subtle shadow
    img = add_soft_shadow(img, blur_radius=8, opacity=80)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'disconnect.png'))
    return img

def create_settings_icon(size=64, bg_color=COLORS['primary'], bg_gradient=COLORS['primary_gradient_end'], fg_color=COLORS['white']):
    """Create an elegant settings icon in lovable.ai style"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient for background
    padding = size // 8
    circle_size = size - 2 * padding
    gradient = create_gradient(circle_size, circle_size, bg_color, bg_gradient)
    
    # Create circle mask
    mask = Image.new('L', (circle_size, circle_size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, circle_size, circle_size), fill=255)
    
    # Apply mask to gradient
    circle_img = gradient.copy()
    circle_img.putalpha(mask)
    
    # Paste the circle
    img.paste(circle_img, (padding, padding), circle_img)
    
    # Draw a more elegant gear with smooth edges
    center = size // 2
    outer_radius = size // 3
    inner_radius = size // 5
    teeth = 10  # More teeth for smoother look
    
    path = []
    for i in range(teeth * 2):
        angle = i * math.pi / teeth
        if i % 2 == 0:
            # Outer point
            r = outer_radius
        else:
            # Inner point
            r = inner_radius
            
        x = center + r * math.cos(angle)
        y = center + r * math.sin(angle)
        path.append((x, y))
    
    # Create a mask for the gear
    gear_mask = Image.new('L', (size, size), 0)
    gear_mask_draw = ImageDraw.Draw(gear_mask)
    
    # Draw the gear on the mask
    gear_mask_draw.polygon(path, fill=255)
    
    # Create a white gear
    gear_img = Image.new('RGBA', (size, size), fg_color)
    gear_img.putalpha(gear_mask)
    
    # Paste the gear onto the main image
    img.paste(gear_img, (0, 0), gear_img)
    
    # Draw center circle with gradient
    center_radius = size // 9
    center_circle = Image.new('RGBA', (center_radius*2, center_radius*2), (0, 0, 0, 0))
    center_circle_draw = ImageDraw.Draw(center_circle)
    
    # Create a mini gradient for the center
    mini_gradient = create_gradient(center_radius*2, center_radius*2, bg_color, bg_gradient)
    
    # Create a circular mask for the center
    center_mask = Image.new('L', (center_radius*2, center_radius*2), 0)
    center_mask_draw = ImageDraw.Draw(center_mask)
    center_mask_draw.ellipse((0, 0, center_radius*2, center_radius*2), fill=255)
    
    # Apply mask to mini gradient
    mini_gradient.putalpha(center_mask)
    
    # Paste the center circle
    img.paste(mini_gradient, (center-center_radius, center-center_radius), mini_gradient)
    
    # Add a subtle shadow
    img = add_soft_shadow(img, blur_radius=8, opacity=80)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'settings.png'))
    return img

def create_tray_icon(size=64, bg_color=COLORS['primary'], bg_gradient=COLORS['primary_gradient_end'], fg_color=COLORS['white']):
    """Create an elegant tray icon in lovable.ai style"""
    # Create image with transparent background
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient for background
    padding = size // 8
    square_size = size - 2 * padding
    rounded_rect_radius = square_size // 4  # More rounded for elegance
    
    # Create gradient
    gradient = create_gradient(square_size, square_size, bg_color, bg_gradient)
    
    # Apply gradient to rounded rectangle
    create_rounded_rectangle(draw, 
                            (padding, padding, size - padding, size - padding), 
                            rounded_rect_radius, 
                            gradient=gradient)
    
    # Draw VPN shield with a more elegant shape
    shield_padding = size // 4
    shield_width = size - 2 * shield_padding
    shield_height = int(shield_width * 1.2)
    
    # Create a more elegant shield shape with smooth curves
    shield_img = Image.new('RGBA', (shield_width, shield_height), (0, 0, 0, 0))
    shield_draw = ImageDraw.Draw(shield_img)
    
    # Shield outline with a more elegant shape
    shield_points = [
        (0, 0),  # Top left
        (shield_width, 0),  # Top right
        (shield_width, shield_height - shield_height // 2.5),  # Bottom right curve start
        (shield_width // 2, shield_height),  # Bottom middle
        (0, shield_height - shield_height // 2.5),  # Bottom left curve start
    ]
    
    # Fill shield with white
    shield_draw.polygon(shield_points, fill=fg_color)
    
    # Add some depth with a subtle inner shadow
    shadow_points = [
        (shield_width // 10, shield_height // 10),  # Top left
        (shield_width - shield_width // 10, shield_height // 10),  # Top right
        (shield_width - shield_width // 10, shield_height - shield_height // 2.2),  # Bottom right
        (shield_width // 2, shield_height - shield_height // 10),  # Bottom middle
        (shield_width // 10, shield_height - shield_height // 2.2),  # Bottom left
    ]
    
    # Paste the shield onto the main image
    img.paste(shield_img, (shield_padding, shield_padding), shield_img)
    
    # Add a lock symbol instead of a simple line for a more VPN-like appearance
    lock_width = size // 3
    lock_height = lock_width * 1.2
    lock_x = (size - lock_width) // 2
    lock_y = (size - lock_height) // 2 + size // 10
    
    # Lock body
    lock_radius = lock_width // 4
    create_rounded_rectangle(draw, 
                            (lock_x, lock_y + lock_width // 2, 
                             lock_x + lock_width, lock_y + lock_height),
                            lock_radius, bg_color)
    
    # Lock arc
    arc_width = lock_width // 2
    arc_height = lock_width // 2
    arc_x = lock_x + lock_width // 4
    arc_y = lock_y
    arc_thickness = lock_width // 6
    
    # Draw arc as the top of the lock
    draw.arc((arc_x, arc_y, arc_x + arc_width, arc_y + arc_height), 
             180, 0, fill=bg_color, width=arc_thickness)
    
    # Add a subtle shadow
    img = add_soft_shadow(img, blur_radius=6, opacity=70)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'tray_icon.png'))
    return img

def create_logo(size=128, bg_color=COLORS['primary'], bg_gradient=COLORS['primary_gradient_end'], fg_color=COLORS['white']):
    """Create an elegant logo in lovable.ai style"""
    # Create image with transparent background - wider for the logo
    width = size * 2
    height = size
    img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create gradient for background
    padding = size // 8
    rect_width = width - 2 * padding
    rect_height = height - 2 * padding
    rounded_rect_radius = rect_height // 4  # More rounded for elegance
    
    # Create horizontal gradient
    gradient = create_gradient(rect_width, rect_height, bg_color, bg_gradient)
    
    # Apply gradient to rounded rectangle
    create_rounded_rectangle(draw, 
                            (padding, padding, width - padding, height - padding), 
                            rounded_rect_radius, 
                            gradient=gradient)
    
    # Draw a more elegant shield on the left
    shield_padding = size // 4
    shield_left = shield_padding * 1.2  # Adjusted for better placement
    shield_top = padding + size // 10
    shield_width = size - 2 * (shield_padding - padding) * 0.8  # Slightly wider
    shield_height = int(shield_width * 1.2)
    
    # Create shield with smoother curves
    shield_img = Image.new('RGBA', (int(shield_width), int(shield_height)), (0, 0, 0, 0))
    shield_draw = ImageDraw.Draw(shield_img)
    
    # Shield points with smoother curves
    shield_points = [
        (0, 0),  # Top left
        (shield_width, 0),  # Top right
        (shield_width, shield_height - shield_height // 2.5),  # Bottom right curve start
        (shield_width // 2, shield_height),  # Bottom middle
        (0, shield_height - shield_height // 2.5),  # Bottom left curve start
    ]
    
    # Fill shield with white
    shield_draw.polygon(shield_points, fill=fg_color)
    
    # Add a subtle inner shadow for depth
    shadow_color = hex_to_rgba(bg_color, 30)  # Semi-transparent shadow
    inner_shield_points = [
        (shield_width // 12, shield_height // 12),
        (shield_width - shield_width // 12, shield_height // 12),
        (shield_width - shield_width // 12, shield_height - shield_height // 2.2),
        (shield_width // 2, shield_height - shield_height // 12),
        (shield_width // 12, shield_height - shield_height // 2.2),
    ]
    
    # Paste shield onto main image
    img.paste(shield_img, (int(shield_left), int(shield_top)), shield_img)
    
    # VPN text with a modern font
    text_x = size + padding * 2
    text_y = size // 2 - size // 8
    
    # Draw "VPN" text with a more elegant appearance
    try:
        # Try to use a nice font if available
        font = ImageFont.truetype("Arial.ttf", size // 3)
    except:
        # Fallback to default
        font = ImageFont.load_default()
    
    # Draw text with a slight shadow for depth
    shadow_offset = size // 50
    draw.text((text_x + shadow_offset, text_y + shadow_offset), "VPN", 
              fill=hex_to_rgba(bg_color, 40), font=font)
    draw.text((text_x, text_y), "VPN", fill=fg_color, font=font)
    
    # Add a subtle shadow to the entire logo
    img = add_soft_shadow(img, blur_radius=10, opacity=60)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'logo.png'))
    return img

def create_dropdown_arrow(size=24, color=COLORS['primary'], gradient_color=COLORS['primary_gradient_end']):
    """Create an elegant dropdown arrow icon in lovable.ai style"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Create smoother triangle points
    padding = size // 6
    points = [
        (size // 4, size // 3),
        (3 * size // 4, size // 3),
        (size // 2, 2 * size // 3)
    ]
    
    # Create gradient for the arrow
    gradient_height = size // 3
    gradient_width = size // 2
    gradient_x = size // 4
    gradient_y = size // 3
    gradient = create_gradient(gradient_width, gradient_height, color, gradient_color)
    
    # Create mask for the gradient
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.polygon(points, fill=255)
    
    # Create arrow with gradient
    arrow = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    arrow.paste(gradient, (gradient_x, gradient_y))
    arrow.putalpha(mask)
    
    # Add a subtle glow
    arrow_glow = arrow.filter(ImageFilter.GaussianBlur(1))
    img.paste(arrow_glow, (0, 0), arrow_glow)
    
    # Paste the actual arrow
    img.paste(arrow, (0, 0), arrow)
    
    # Save the image
    img.save(os.path.join(SAVE_DIR, 'dropdown_arrow.png'))
    return img

def create_status_icons(size=16):
    """Create elegant status indicator icons"""
    # Connected status with gradient
    connected_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    gradient = create_gradient(size, size, COLORS['success'], COLORS['success_gradient_end'])
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    gradient.putalpha(mask)
    connected_img = add_soft_shadow(gradient, blur_radius=2, opacity=50)
    connected_img.save(os.path.join(SAVE_DIR, 'status_connected.png'))
    
    # Disconnected status with gradient
    disconnected_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    gradient = create_gradient(size, size, COLORS['danger'], COLORS['danger_gradient_end'])
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    gradient.putalpha(mask)
    disconnected_img = add_soft_shadow(gradient, blur_radius=2, opacity=50)
    disconnected_img.save(os.path.join(SAVE_DIR, 'status_disconnected.png'))
    
    # Connecting status with gradient
    connecting_img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    gradient = create_gradient(size, size, COLORS['warning'], COLORS['warning_gradient_end'])
    mask = Image.new('L', (size, size), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.ellipse((0, 0, size, size), fill=255)
    gradient.putalpha(mask)
    connecting_img = add_soft_shadow(gradient, blur_radius=2, opacity=50)
    connecting_img.save(os.path.join(SAVE_DIR, 'status_connecting.png'))

if __name__ == "__main__":
    print("Generating elegant lovable.ai style icons...")
    try:
        create_connect_icon()
        create_disconnect_icon()
        create_settings_icon()
        create_tray_icon()
        create_logo()
        create_dropdown_arrow()
        create_status_icons()
        print(f"Icons generated and saved to {SAVE_DIR}")
        print("✨ Elegance achieved! Icons are now ready to use.")
    except Exception as e:
        print(f"Error generating icons: {e}")