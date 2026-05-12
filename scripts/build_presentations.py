from pathlib import Path
import markdown
import re


# =========================
# CONFIG
# =========================

CONTENT_DIR = Path("docs")
OUTPUT_FILE = Path("docs/slides.html")

TYPE_PATTERN = re.compile(r"<!--\s*type:\s*(\w+)\s*-->")


# =========================
# LOAD ALL MARKDOWN
# =========================

def get_markdown_files():
    return sorted(CONTENT_DIR.rglob("*.md"))


# =========================
# PARSE TYPE BLOCKS
# =========================

def parse_blocks(text):
    parts = TYPE_PATTERN.split(text)

    if len(parts) < 2:
        return [("content", text)]

    blocks = []

    if parts[0].strip():
        blocks.append(("content", parts[0].strip()))

    for i in range(1, len(parts), 2):
        block_type = parts[i].strip()
        block_content = parts[i + 1].strip()
        blocks.append((block_type, block_content))

    return blocks


# =========================
# BUILD SLIDES
# =========================

def build_slides():
    slides = []

    files = get_markdown_files()

    print(f"📄 Found {len(files)} markdown files")

    for file in files:

        text = file.read_text(encoding="utf-8")
        blocks = parse_blocks(text)

        # file title slide
        slides.append(f"""
        <section>
            <h1>{file.stem.replace('-', ' ').title()}</h1>
        </section>
        """)

        for block_type, content in blocks:

            html = markdown.markdown(content, extensions=[
                "fenced_code",
                "tables",
                "sane_lists"
            ])

            slides.append(f"""
            <section class="{block_type}">
                {html}
            </section>
            """)

    return slides


# =========================
# WRAP REVEAL
# =========================

def wrap(slides_html):

    return f"""
<!doctype html>
<html>
<head>
<meta charset="utf-8">

<title>Workshop Slides</title>

<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.css">
<link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js/dist/theme/white.css">

<style>
body {{
    font-family: sans-serif;
}}

section {{
    text-align: left;
}}

section.exercise {{
    background: #fff3cd;
}}

section.concept {{
    background: #e8f4ff;
}}

section.reflection {{
    background: #f3f3f3;
}}

section.framework {{
    background: #eef7f1;
}}

h1, h2, h3 {{
    color: #004b6c;
}}
</style>

</head>

<body>

<div class="reveal">
<div class="slides">

{''.join(slides_html)}

</div>
</div>

<script src="https://cdn.jsdelivr.net/npm/reveal.js/dist/reveal.js"></script>

<script>
Reveal.initialize({{
    hash: true,
    slideNumber: true,
    margin: 0.05,
    minScale: 0.2,
    maxScale: 1.2
}});
</script>

</body>
</html>
"""


# =========================
# RUN
# =========================

def main():

    slides = build_slides()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    OUTPUT_FILE.write_text(wrap(slides), encoding="utf-8")

    print(f"\n✅ Built single slide deck:")
    print(f"   {OUTPUT_FILE}")


if __name__ == "__main__":
    main()