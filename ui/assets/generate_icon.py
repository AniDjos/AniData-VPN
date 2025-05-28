#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AniData VPN - Icon Generator
# © 2023 AniData - All Rights Reserved

import os
import sys
from PIL import Image, ImageDraw, ImageFont

def create_vpn_icon(size=512, output_path="icon.png"):
    """
    Create a VPN icon with blue azur color and shield design
    
    Args:
        size (int): Size of the icon in pixels
        output_path (str): Path to save the icon
    """
    # Create a new image with transparent background
    img = Image.new('RGBA', (size, size), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Define colors
    blue_azur = (0, 127, 255)      # #007FFF
    light_blue = (77, 166, 255)    # #4DA6FF
    white = (255, 255, 255)        # #FFFFFF
    
    # Draw shield shape
    shield_margin = size // 10
    shield_width = size - (2 * shield_margin)
    shield_height = int(shield_width * 1.2)
    
    # Shield coordinates
    left = shield_margin
    top = shield_margin
    right = left + shield_width
    bottom = min(top + shield_height, size - shield_margin)
    
    # Draw main shield (rounded rectangle with pointed bottom)
    radius = shield_width // 8
    
    # Draw shield background
    points = [
        (left + radius, top),  # Top left after corner
        (right - radius, top),  # Top right before corner
        (right, top + radius),  # Right top after corner
        (right, top + shield_height * 0.7),  # Right side
        ((left + right) // 2, bottom),  # Bottom point
        (left, top + shield_height * 0.7),  # Left side
        (left, top + radius),  # Left top after corner
    ]
    
    # Draw main shield with blue azur gradient
    for y in range(top, bottom):
        # Calculate progress from top to bottom (0.0 to 1.0)
        progress = (y - top) / (bottom - top)
        
        # Calculate color at this position (gradient from blue_azur to light_blue)
        r = int(blue_azur[0] + progress * (light_blue[0] - blue_azur[0]))
        g = int(blue_azur[1] + progress * (light_blue[1] - blue_azur[1]))
        b = int(blue_azur[2] + progress * (light_blue[2] - blue_azur[2]))
        
        # Draw a horizontal line at this position
        draw.line([(left, y), (right, y)], fill=(r, g, b))
    
    # Draw shield outline
    draw.polygon(points, outline=blue_azur)
    
    # Draw VPN network symbol (simple network/lock icon)
    center_x = size // 2
    center_y = size // 2
    icon_size = shield_width // 2
    
    # Draw a globe-like network symbol
    network_radius = icon_size // 2
    
    # Horizontal lines (latitude lines)
    for i in range(3):
        y_offset = -network_radius + (i * network_radius)
        ellipse_height = network_radius // 2
        draw.ellipse((center_x - network_radius, center_y + y_offset - ellipse_height//2, 
                     center_x + network_radius, center_y + y_offset + ellipse_height//2), 
                     outline=white, width=max(2, size//100))
    
    # Vertical line (longitude)
    draw.line([(center_x, center_y - network_radius), 
               (center_x, center_y + network_radius)], 
               fill=white, width=max(2, size//100))
    
    # Lock shape at the bottom
    lock_size = icon_size // 2
    lock_top = center_y + network_radius - lock_size // 2
    lock_left = center_x - lock_size // 2
    
    # Lock body (rectangle)
    draw.rectangle((lock_left, lock_top + lock_size//3, 
                   lock_left + lock_size, lock_top + lock_size),
                   fill=white, outline=blue_azur)
    
    # Lock shackle (U shape)
    shackle_width = lock_size // 3
    draw.arc((lock_left + shackle_width, lock_top - shackle_width, 
             lock_left + lock_size - shackle_width, lock_top + shackle_width),
             180, 0, fill=white, width=max(2, size//100))
    
    draw.line([(lock_left + shackle_width, lock_top), 
               (lock_left + shackle_width, lock_top + lock_size//3)], 
               fill=white, width=max(2, size//100))
    
    draw.line([(lock_left + lock_size - shackle_width, lock_top), 
               (lock_left + lock_size - shackle_width, lock_top + lock_size//3)], 
               fill=white, width=max(2, size//100))
    
    # Add "VPN" text at the top of the shield
    try:
        # Try to load a font
        font_size = shield_width // 4
        try:
            font = ImageFont.truetype("Arial.ttf", font_size)
        except:
            try:
                font = ImageFont.truetype("DejaVuSans.ttf", font_size)
            except:
                font = ImageFont.load_default()
        
        # Calculate text position
        text = "VPN"
        text_width, text_height = draw.textsize(text, font=font) if hasattr(draw, 'textsize') else font.getsize(text)
        text_x = center_x - text_width // 2
        text_y = top + shield_width // 8
        
        # Draw text
        draw.text((text_x, text_y), text, fill=white, font=font)
    except Exception as e:
        print(f"Could not add text to icon: {e}")
    
    # Save the image
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    img.save(output_path)
    print(f"Icon saved to {output_path}")
    
    # Return the image for further use
    return img

def generate_icons_for_all_platforms():
    """Generate icons for all supported platforms"""
    # Create directory for icons
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icons_dir = os.path.join(script_dir, "icons")
    os.makedirs(icons_dir, exist_ok=True)
    
    # Base icon
    base_icon = create_vpn_icon(512, os.path.join(script_dir, "icon.png"))
    
    # Windows ICO file (needs multiple sizes)
    ico_sizes = [16, 24, 32, 48, 64, 128, 256]
    ico_images = []
    for size in ico_sizes:
        resized_img = base_icon.resize((size, size), Image.LANCZOS)
        ico_images.append(resized_img)
    
    # Save ICO file
    ico_path = os.path.join(icons_dir, "anidata_vpn.ico")
    ico_images[0].save(ico_path, sizes=[(img.width, img.height) for img in ico_images], format='ICO')
    print(f"Windows icon saved to {ico_path}")
    
    # Linux PNG files
    linux_sizes = [16, 24, 32, 48, 64, 128, 256, 512]
    for size in linux_sizes:
        png_path = os.path.join(icons_dir, f"anidata_vpn_{size}x{size}.png")
        base_icon.resize((size, size), Image.LANCZOS).save(png_path)
        print(f"Linux icon ({size}x{size}) saved to {png_path}")
    
    # macOS ICNS file - skipping as it requires additional libraries
    print("For macOS, use the PNG files to create an .icns file")

if __name__ == "__main__":
    generate_icons_for_all_platforms()