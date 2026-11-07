import os
import re

with open('app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Find the style block
style_match = re.search(r'<style>(.*?)</style>', content, re.DOTALL)

if style_match:
    style_content = style_match.group(1).strip()
    
    # Create static directory
    os.makedirs('static', exist_ok=True)
    
    # Write to style.css
    with open('static/style.css', 'w', encoding='utf-8') as f:
        f.write(style_content)
        
    # Replace style block with link tag
    link_tag = '<link href="{{ url_for(\'static\', filename=\'style.css\') }}" rel="stylesheet">'
    content = content.replace(style_match.group(0), link_tag)
    
    with open('app.py', 'w', encoding='utf-8') as f:
        f.write(content)
        
    print("CSS extracted successfully.")
else:
    print("No style block found.")
