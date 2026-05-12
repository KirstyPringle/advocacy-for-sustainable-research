#!/usr/bin/env python3
"""
Convert markdown files from docs/green-change/ to Reveal.js HTML presentations.
Reads markdown files from docs directory and outputs to presentations/

Usage: python scripts/markdown_to_reveal.py
"""

import os
from pathlib import Path
import re

def markdown_to_reveal(markdown_file, output_file):
    """
    Convert markdown with --- separators to Reveal.js HTML presentations.
    Reads from docs/ and outputs to presentations/
    """
    
    with open(markdown_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Split by --- to get individual slides
    slides = content.split('\n---\n')
    
    slide_html = []
    for slide in slides:
        slide = slide.strip()
        if not slide:
            continue
        # Wrap each slide in a section
        slide_html.append(f'<section>\n{slide}\n</section>')
    
    # Get title from filename
    title = Path(markdown_file).stem.replace('_', ' ').title()
    
    # Create HTML document
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} — Green Change Workshop</title>
    <link rel="stylesheet" href="../reveal/dist/reveal.css">
    <link rel="stylesheet" href="../reveal/dist/theme/white.css">
    <link rel="stylesheet" href="../presentation.css">
</head>
<body>
    <div id="presentation-content">
    <a class="back-link" href="../presentations/">← Back to workbook</a>

    <div class="reveal">
        <div class="slides">
            {''.join(slide_html)}
        </div>
    </div>

    </div><!-- end presentation-content -->

    <script src="../reveal/dist/reveal.js"></script>
    <script src="../reveal/plugin/notes/notes.js"></script>
    <script src="../presentation.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/mermaid/dist/mermaid.min.js"></script>
    <script>
        mermaid.initialize({{ startOnLoad: false, theme: 'default' }});

        function renderMermaidOnSlide(slide) {{
            var diagrams = slide.querySelectorAll('.mermaid:not([data-processed])');
            if (diagrams.length) {{
                mermaid.run({{ nodes: diagrams }});
            }}
        }}

        if (Reveal.isReady()) {{
            renderMermaidOnSlide(Reveal.getCurrentSlide());
        }} else {{
            Reveal.on('ready', function () {{
                renderMermaidOnSlide(Reveal.getCurrentSlide());
            }});
        }}

        Reveal.on('slidechanged', function (event) {{
            renderMermaidOnSlide(event.currentSlide);
        }});
    </script>
</body>
</html>"""
    
    # Write output file
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html)
    
    print(f"✓ Generated {output_file}")

def main():
    """
    Convert all markdown files in docs/green-change/ to presentations/
    """
    
    source_dir = Path('docs/green-change')
    presentations_dir = Path('presentations')
    
    if not source_dir.exists():
        print(f"Error: {source_dir} directory not found")
        return
    
    # Get all markdown files and sort them
    md_files = sorted(source_dir.glob('*.md'))
    
    if not md_files:
        print(f"No markdown files found in {source_dir}")
        return
    
    # Process all markdown files
    for md_file in md_files:
        # Skip index.md
        if md_file.name == 'index.md':
            continue
        
        output_file = presentations_dir / f"{md_file.stem}.html"
        markdown_to_reveal(str(md_file), str(output_file))
    
    print(f"\n✓ All slides generated in {presentations_dir}/")
    print(f"\nTo view slides, open any .html file in your browser")

if __name__ == '__main__':
    main()
