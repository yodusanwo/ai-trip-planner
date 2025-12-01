"""
Generate preview images for social media sharing.

This script creates og-image.png and twitter-image.png for use in
Open Graph and Twitter Card meta tags.

Requirements:
    pip install pillow

Usage:
    python generate_preview.py
"""

from PIL import Image, ImageDraw, ImageFont
import os

def create_preview_image(output_path="og-image.png"):
    """Create a preview image for social media"""
    
    # Image dimensions (Open Graph standard)
    width = 1200
    height = 630
    
    # Create image with gradient background
    img = Image.new('RGB', (width, height))
    draw = ImageDraw.Draw(img)
    
    # Create gradient background (purple to blue)
    for y in range(height):
        # Calculate color for this row
        ratio = y / height
        r = int(102 + (118 - 102) * ratio)  # 667eea to 764ba2
        g = int(126 + (75 - 126) * ratio)
        b = int(234 + (162 - 234) * ratio)
        
        # Draw horizontal line with this color
        draw.rectangle([(0, y), (width, y+1)], fill=(r, g, b))
    
    # Try to load fonts, fall back to default if not available
    try:
        title_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 90)
        subtitle_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 40)
        feature_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 28)
        footer_font = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 32)
    except:
        print("⚠️  Could not load system fonts, using default")
        title_font = ImageFont.load_default()
        subtitle_font = ImageFont.load_default()
        feature_font = ImageFont.load_default()
        footer_font = ImageFont.load_default()
    
    # Add emoji icon (using text)
    icon = "✈️"
    icon_bbox = draw.textbbox((0, 0), icon, font=title_font)
    icon_width = icon_bbox[2] - icon_bbox[0]
    draw.text(((width - icon_width) // 2, 80), icon, fill='white', font=title_font)
    
    # Add title
    title = "AI Trip Planner"
    title_bbox = draw.textbbox((0, 0), title, font=title_font)
    title_width = title_bbox[2] - title_bbox[0]
    draw.text(((width - title_width) // 2, 200), title, fill='white', font=title_font)
    
    # Add subtitle
    subtitle = "Plan Your Perfect Trip with AI Agents"
    subtitle_bbox = draw.textbbox((0, 0), subtitle, font=subtitle_font)
    subtitle_width = subtitle_bbox[2] - subtitle_bbox[0]
    draw.text(((width - subtitle_width) // 2, 300), subtitle, fill='white', font=subtitle_font)
    
    # Add features
    features = ["🤖 Multi-Agent AI", "⚡ 45s - 2.5min", "📄 HTML Itineraries"]
    feature_y = 380
    feature_spacing = 200
    start_x = (width - (len(features) * feature_spacing)) // 2
    
    for i, feature in enumerate(features):
        # Draw feature box background
        feature_bbox = draw.textbbox((0, 0), feature, font=feature_font)
        feature_width = feature_bbox[2] - feature_bbox[0]
        feature_height = feature_bbox[3] - feature_bbox[1]
        
        box_x = start_x + (i * feature_spacing)
        box_y = feature_y
        box_padding = 15
        
        # Draw semi-transparent box
        draw.rounded_rectangle(
            [(box_x - box_padding, box_y - box_padding), 
             (box_x + feature_width + box_padding, box_y + feature_height + box_padding)],
            radius=10,
            fill=(255, 255, 255, 40),
            outline=(255, 255, 255, 60),
            width=2
        )
        
        # Draw feature text
        draw.text((box_x, box_y), feature, fill='white', font=feature_font)
    
    # Add footer
    footer = "Created by Zora Digital"
    footer_bbox = draw.textbbox((0, 0), footer, font=footer_font)
    footer_width = footer_bbox[2] - footer_bbox[0]
    draw.text(((width - footer_width) // 2, 500), footer, fill='white', font=footer_font)
    
    # Add badge
    badge = "AI Agent Showcase"
    badge_bbox = draw.textbbox((0, 0), badge, font=feature_font)
    badge_width = badge_bbox[2] - badge_bbox[0]
    badge_height = badge_bbox[3] - badge_bbox[1]
    
    badge_x = (width - badge_width) // 2
    badge_y = 560
    badge_padding = 10
    
    draw.rounded_rectangle(
        [(badge_x - badge_padding, badge_y - badge_padding),
         (badge_x + badge_width + badge_padding, badge_y + badge_height + badge_padding)],
        radius=20,
        fill=(255, 255, 255, 50),
        outline=(255, 255, 255, 80),
        width=1
    )
    
    draw.text((badge_x, badge_y), badge, fill='white', font=feature_font)
    
    # Save image
    img.save(output_path, 'PNG', quality=95)
    print(f"✅ Created: {output_path}")
    
    return img

if __name__ == "__main__":
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    print("🎨 Generating preview images...")
    print()
    
    # Create Open Graph image
    og_path = os.path.join(script_dir, "og-image.png")
    create_preview_image(og_path)
    
    # Create Twitter image (same as OG for now)
    twitter_path = os.path.join(script_dir, "twitter-image.png")
    create_preview_image(twitter_path)
    
    print()
    print("✨ Done! Preview images created successfully.")
    print()
    print("Next steps:")
    print("1. Review the images")
    print("2. Commit them to your repo")
    print("3. Push to GitHub")
    print("4. Images will be automatically used for social sharing!")

