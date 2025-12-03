#!/usr/bin/env python3
"""
Extract slides from Genspark HTML file and create a clean HTML for PDF export.
"""

import re
import html
from pathlib import Path

def extract_slides(input_file, output_file):
    """Extract slides from the Genspark HTML and create a clean export file."""
    
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract @font-face declarations
    font_faces = []
    font_face_pattern = r'@font-face\{[^}]+\}'
    font_faces = re.findall(font_face_pattern, content)
    
    # Extract all style blocks to get Tailwind utilities and other styles
    # Only get the first occurrence of the large Tailwind style block to avoid duplication
    style_pattern = r'<style[^>]*>(.*?)</style>'
    style_matches = re.findall(style_pattern, content, re.DOTALL)
    
    # Combine styles - filter to get unique styles
    seen_styles = set()
    unique_styles = []
    for style in style_matches:
        # Skip if we've seen this exact style before
        if style not in seen_styles and len(style) > 100:  # Only include substantial style blocks
            seen_styles.add(style)
            unique_styles.append(style)
    
    all_styles = '\n'.join(unique_styles)
    
    # Extract slides - they are between <body> tags and contain slide-container divs
    # We need to extract just the slide-container div and its content
    body_splits = content.split('<body>')
    
    slides = []
    for i, section in enumerate(body_splits[1:], 1):  # Skip the first part (before first <body>)
        # Check if this contains a slide
        if 'slide-container' not in section:
            continue
        
        # Unescape HTML entities first
        slide_html = html.unescape(section)
        
        # Find the slide-container div
        container_start = slide_html.find('<div class="slide-container')
        if container_start < 0:
            continue
        
        # Find the closing div for the slide-container
        # We need to find the matching closing tag
        # Start from the container_start and count opening/closing divs
        div_count = 0
        pos = container_start
        container_end = -1
        
        while pos < len(slide_html):
            # Look for next div tag
            next_open = slide_html.find('<div', pos)
            next_close = slide_html.find('</div>', pos)
            
            if next_close < 0:
                # No more closing divs
                break
            
            if next_open >= 0 and next_open < next_close:
                # Found an opening div before the closing one
                div_count += 1
                pos = next_open + 4
            else:
                # Found a closing div
                if div_count == 0:
                    # This is the closing tag for our slide-container
                    container_end = next_close + 6  # Include </div>
                    break
                else:
                    div_count -= 1
                    pos = next_close + 6
        
        if container_end > container_start:
            # Extract just the slide-container div
            slide_content = slide_html[container_start:container_end]
            slides.append(slide_content.strip())
    
    print(f"Found {len(slides)} slides")
    
    # Build the output HTML
    output_html = f"""<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=1280, initial-scale=1.0">
    <title>Академічний плагіат - Експорт слайдів</title>
    
    <style>
        /* Font faces */
        {chr(10).join(font_faces)}
        
        /* All extracted styles */
        {all_styles}
        
        /* Print styles */
        @page {{
            size: 1280px 720px landscape;
            margin: 0;
        }}
        
        body {{
            margin: 0;
            padding: 0;
            background: #000;
            -webkit-print-color-adjust: exact !important;
            print-color-adjust: exact !important;
            color-adjust: exact !important;
        }}
        
        .slide {{
            width: 1280px;
            height: 720px;
            page-break-after: always;
            break-after: page;
            page-break-inside: avoid;
            break-inside: avoid;
            position: relative;
            overflow: hidden;
        }}
        
        .slide:last-child {{
            page-break-after: auto;
        }}
        
        @media print {{
            .print-btn {{ 
                display: none !important; 
            }}
            body {{ 
                -webkit-print-color-adjust: exact !important;
                print-color-adjust: exact !important;
                color-adjust: exact !important;
            }}
        }}
        
        .print-btn {{
            position: fixed;
            top: 20px;
            right: 20px;
            padding: 15px 30px;
            background: #4CAF50;
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 18px;
            cursor: pointer;
            z-index: 9999;
            box-shadow: 0 4px 15px rgba(0,0,0,0.3);
        }}
        
        .print-btn:hover {{
            background: #45a049;
        }}
    </style>
</head>
<body>
    <button onclick="window.print()" class="print-btn">🖨️ Печать в PDF</button>
    
"""
    
    # Add each slide
    for i, slide_content in enumerate(slides, 1):
        output_html += f'    <div class="slide">\n{slide_content}\n    </div>\n'
    
    output_html += """</body>
</html>"""
    
    # Write the output file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(output_html)
    
    print(f"Created {output_file} with {len(slides)} slides")

if __name__ == '__main__':
    input_file = Path('Genspark (03.12.2025 07：41：35).html')
    output_file = Path('slides-export-plagiat.html')
    
    if not input_file.exists():
        print(f"Error: {input_file} not found")
        exit(1)
    
    extract_slides(input_file, output_file)
    print("Done!")
