import re
from pathlib import Path
import markdown

# =========================
# CONFIG
# =========================

##OUTPUT_DIR = Path("slides")
OUTPUT_DIR = Path("docs/slides")
OUTPUT_FILE = OUTPUT_DIR / "green-change-workshop.html"

MANIFEST_FILE = Path("scripts/slides_sources.txt")

TYPE_PATTERN = re.compile(r"<!--\s*type:\s*(\w+)\s*-->")
END_TYPE_PATTERN = re.compile(r"<!--\s*end:\s*type\s*-->", re.IGNORECASE)

# =========================
# LOAD MANIFEST
# =========================

def load_sources():
    if not MANIFEST_FILE.exists():
        raise FileNotFoundError(f"Missing manifest: {MANIFEST_FILE}")

    with open(MANIFEST_FILE, "r", encoding="utf-8") as f:
        return [
            line.strip()
            for line in f
            if line.strip() and not line.strip().startswith("#")
        ]

# =========================
# EXTRACT TITLE
# =========================

def extract_title_from_md(text: str) -> str:
    """Extract the first H1 heading from markdown, or return formatted filename if not found."""
    # Look for first line starting with "# " (H1 heading)
    for line in text.split('\n'):
        if line.strip().startswith('# '):
            return line.strip()[2:].strip()
    # Fallback to filename-based title if no H1 found
    return None

# =========================
# PARSE MARKDOWN
# =========================

def parse_file(path: Path):

    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")

    slides = []

    # Find all type blocks between <!-- type: xxx --> and <!-- end: type -->
    for match in TYPE_PATTERN.finditer(text):
        block_type = match.group(1).strip()
        start_pos = match.end()
        
        # Find the corresponding end tag
        end_match = END_TYPE_PATTERN.search(text, start_pos)
        if not end_match:
            continue
        
        end_pos = end_match.start()
        content = text[start_pos:end_pos].strip()
        
        if not content:
            continue
        
        # Fix image paths: make them relative from slides/ to docs/green-change/
        content = re.sub(
            r'!\[([^\]]*)\]\(([^)]+\.png)\)',
            r'![\1](../docs/green-change/\2)',
            content
        )
        
        # Clean up MkDocs admonition syntax
        # Convert !!! type "title" to bold headings
        content = re.sub(
            r'^!!!\s+(\w+)\s+"([^"]+)"',
            r'**\2**',
            content,
            flags=re.MULTILINE
        )
        # Remove remaining !!! lines
        content = re.sub(r'^\s*!!!\s+\w+\s*$', '', content, flags=re.MULTILINE)
        # Remove tab-indented content after admonitions
        content = re.sub(r'\n\t+', '\n', content)

        # Split block into sections by ##, ###, and <!-- slide break -->
        # First split by <!-- slide break --> (explicit breaks)
        sections_by_break = content.split('<!-- slide break -->')
        
        break_count = len(sections_by_break) - 1
        if break_count > 0:
            print(f"  ℹ️ Found {break_count} slide break(s)")
        
        for break_idx, section_by_break in enumerate(sections_by_break):
            section_by_break = section_by_break.strip()
            
            # Then split by ## (h2)
            sections_h2 = re.split(r"(?=^##\s+)", section_by_break, flags=re.MULTILINE)

            for section_h2 in sections_h2:
                section_h2 = section_h2.strip()
                if not section_h2:
                    continue
                
                # Further split by ### if they exist
                sections_h3 = re.split(r"(?=^###\s+)", section_h2, flags=re.MULTILINE)
                
                for section_h3 in sections_h3:
                    section_h3 = section_h3.strip()
                    if not section_h3:
                        continue
                    
                    # Check for <!-- small --> marker within this section
                    small = "<!-- small -->" in section_h3
                    section_h3 = section_h3.replace("<!-- small -->", "").strip()

                    slides.append((block_type, section_h3, small))

    return slides

# =========================
# HTML WRAPPER
# =========================

def wrap_reveal(all_slides):

    html = [
        "<!doctype html>",
        "<html>",
        "<head>",
        "<meta charset='utf-8'>",
        "<title>Green Change Workshop</title>",

        "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css'>",
        "<link rel='stylesheet' href='https://cdn.jsdelivr.net/npm/reveal.js/dist/theme/white.css'>",

        "<style>",

        """
        body {
            font-family: sans-serif;
        }

        .reveal section {
            text-align: left;
            overflow-y: auto;
            max-height: 95vh;
            padding: 1rem;
        }

        section[data-type="concept"] {
            background: #ffffff;
        }

        section[data-type="exercise"] {
            background: #fff3cd;
        }

        section[data-type="framework"] {
            background: #e8f4ff;
        }

        section[data-type="reflection"] {
            background: #f3f3f3;
        }

        h1, h2, h3 {
            color: #004b6c;
            margin-top: 0.5rem;
            margin-bottom: 0.5rem;
        }

        ul, ol {
            margin-left: 1.2rem;
        }

        p, li {
            font-size: 0.85em;
            line-height: 1.4;
            margin: 0.2rem 0;
        }
        
        img {
            max-width: 85%;
            max-height: 55vh;
            width: auto;
            height: auto;
            margin: 1.5rem auto;
            display: block;
            border-radius: 4px;
            object-fit: contain;
        }
        
        pre {
            max-width: 100%;
            font-size: 0.75em;
            padding: 0.5rem;
            background: #f5f5f5;
            border-radius: 4px;
            overflow-x: auto;
        }
        
        code {
            background: #f0f0f0;
            padding: 0.2em 0.4em;
            border-radius: 3px;
            font-size: 0.85em;
        }
        """,

        "</style>",
        "</head>",
        "<body>",

        "<div class='reveal'>",
        "<div class='slides'>"
    ]

    # =========================
    # ADD SLIDES
    # =========================

    for slide in all_slides:

        if slide["kind"] == "title":

            html.append(
                f"""
                <section>
                    <h1>{slide['title']}</h1>
                </section>
                """
            )

        elif slide["kind"] == "content":

            font_style = ' style="font-size: 0.65em;"' if slide.get("small") else ""

            html.append(
                f"""
                <section data-type="{slide['type']}"{font_style}>
                    {slide['content']}
                </section>
                """
            )

    # =========================
    # FOOTER / REVEAL INIT
    # =========================

    html += [

        "</div>",
        "</div>",

        "<script src='https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js'></script>",

        """
        <script>
        Reveal.initialize({
            hash: true,
            slideNumber: true,
            margin: 0.05,
            minScale: 0.2,
            maxScale: 1.2
        });
        </script>
        """,

        "</body>",
        "</html>"
    ]

    return "\n".join(html)

# =========================
# BUILD
# =========================

def build():

    OUTPUT_DIR.mkdir(exist_ok=True)

    sources = load_sources()

    all_slides = []

    print(f"📄 Found {len(sources)} source files")

    for path_str in sources:

        file = Path(path_str)

        print(f"➡️ Processing {file}")

        # Read the file to extract title
        text = file.read_text(encoding="utf-8")
        
        slides = parse_file(file)

        if not slides:
            print(f"⚠️ No slide content in {file}")
            continue

        # Add lesson title slide
        lesson_title = extract_title_from_md(text)
        if not lesson_title:
            lesson_title = file.stem.replace("-", " ").title()

        all_slides.append({
            "kind": "title",
            "title": lesson_title
        })

        # Add lesson content slides

        for block_type, content, small in slides:

            html_content = markdown.markdown(content, extensions=["tables"])

            all_slides.append({
                "kind": "content",
                "type": block_type,
                "content": html_content,
                "small": small,
            })

    # Build final HTML

    html = wrap_reveal(all_slides)

    OUTPUT_FILE.write_text(html, encoding="utf-8")

    print("\n✅ Built combined workshop deck:")
    print(f"   {OUTPUT_FILE}")

# =========================
# RUN
# =========================

if __name__ == "__main__":
    build()