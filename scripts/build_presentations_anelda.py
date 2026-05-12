"""Render presentation HTML files from Jinja2 templates.

Reads Jinja2 templates from docs/presentations/templates/ that use
template inheritance from base.html, and renders the final HTML files
into docs/presentations/.
"""

from pathlib import Path

from jinja2 import Environment, FileSystemLoader


PROJECT_ROOT = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = PROJECT_ROOT / "presentations"
OUTPUT_DIR = PROJECT_ROOT / "docs" / "presentations"


def main() -> None:
    env = Environment(
        loader=FileSystemLoader(TEMPLATE_DIR),
        keep_trailing_newline=True,
    )

    templates = sorted(TEMPLATE_DIR.glob("part-*.html"))
    if not templates:
        print("No presentation templates found.")
        return

    print(f"Rendering {len(templates)} presentation(s):")
    for template_path in templates:
        template = env.get_template(template_path.name)
        output = OUTPUT_DIR / template_path.name
        rendered = template.render()
        if output.exists() and output.read_text(encoding="utf-8") == rendered:
            print(f"  {template_path.name} (unchanged)")
            continue
        output.write_text(rendered, encoding="utf-8")
        print(f"  {template_path.name} -> {output.name}")

    print("Done.")


if __name__ == "__main__":
    main()
