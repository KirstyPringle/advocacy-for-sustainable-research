import re
from pathlib import Path
import markdown

# =========================
# CONFIG
# =========================

OUTPUT_DIR = Path("slides")
OUTPUT_FILE = OUTPUT_DIR / "green-change-workshop.html"

MANIFEST_FILE = Path("scripts/slides_sources.txt")

TYPE_PATTERN = re.compile(r"<!--\s*type:\s*(\w+)\s*-->")

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
# PARSE MARKDOWN
# =========================

def parse_file(path: Path):

    if not path.exists():
        return []

    text = path.read_text(encoding="utf-8")

    # Split into typed blocks
    blocks = TYPE_PATTERN.split(text)

    if len(blocks) < 3:
        return []

    slides = []

    # blocks format:
    # [preamble, type, content, type, content...]

    for i in range(1, len(blocks), 2):

        block_type = blocks[i].strip()
        content = blocks[i + 1].strip()

        # Split block into sections by ##
        sections = re.split(r"(?=^##\s+)", content, flags=re.MULTILINE)

        for section in sections:

            section = section.strip()

            if not section:
                continue

            slides.append((block_type, section))

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
        }

        ul, ol {
            margin-left: 1.2rem;
        }

        p, li {
            font-size: 0.9em;
            line-height: 1.4;
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

            html.append(
                f"""
                <section data-type="{slide['type']}">
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

        slides = parse_file(file)

        if not slides:
            print(f"⚠️ No slide content in {file}")
            continue

        # Add lesson title slide

        lesson_title = file.stem.replace("-", " ").title()

        all_slides.append({
            "kind": "title",
            "title": lesson_title
        })

        # Add lesson content slides

        for block_type, content in slides:

            html_content = markdown.markdown(content)

            all_slides.append({
                "kind": "content",
                "type": block_type,
                "content": html_content
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