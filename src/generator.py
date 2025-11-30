import os
from typing import Callable

from markdown_extract import extract_title
from converter import markdown_to_html_node


def generate_page(from_path: str, template_path: str, dest_path: str, basepath: str = '/', logger: Callable[[str], None] = print):
    """
    Generate an HTML page by converting a markdown file to HTML and injecting it into a template.

    Args:
        from_path: Path to the markdown source file
        template_path: Path to the HTML template containing `{{ Title }}` and `{{ Content }}` placeholders
        dest_path: Destination path for the generated HTML
        logger: Optional logger callable
    """
    logger(f"Generating page from {from_path} to {dest_path} using {template_path}")

    # Read source markdown
    with open(from_path, "r", encoding="utf-8") as f:
        markdown = f.read()

    # Read template
    with open(template_path, "r", encoding="utf-8") as f:
        template = f.read()

    # Convert markdown to HTML string
    root = markdown_to_html_node(markdown)
    content_html = root.to_html()

    # Extract title
    title = extract_title(markdown)

    # Replace placeholders
    page = template.replace("{{ Title }}", title).replace("{{ Content }}", content_html)

    # Normalize basepath to always end with a slash
    if not basepath.endswith('/'):
        basepath = basepath + '/'

    # Replace absolute references to root ("/...") with basepath-prefixed paths
    page = page.replace('href="/', f'href="{basepath}')
    page = page.replace('src="/', f'src="{basepath}')

    # Ensure destination directory exists
    dest_dir = os.path.dirname(dest_path)
    if dest_dir:
        os.makedirs(dest_dir, exist_ok=True)

    # Write out
    with open(dest_path, "w", encoding="utf-8") as f:
        f.write(page)

    logger(f"Wrote {dest_path}")


def generate_pages_recursive(dir_path_content: str, template_path: str, dest_dir_path: str, basepath: str = '/', logger: Callable[[str], None] = print):
    """
    Walk `dir_path_content` and generate an HTML page for every markdown file found.

    The generated .html files are written under `dest_dir_path` preserving the
    directory structure relative to `dir_path_content`.
    """
    if not os.path.isdir(dir_path_content):
        raise FileNotFoundError(f"Content directory not found: {dir_path_content}")

    for root, dirs, files in os.walk(dir_path_content):
        for fname in files:
            if not fname.lower().endswith('.md'):
                continue

            src_path = os.path.join(root, fname)
            # Compute relative path from content dir
            rel_path = os.path.relpath(src_path, dir_path_content)
            # Replace extension with .html
            rel_base, _ = os.path.splitext(rel_path)
            dest_rel = rel_base + '.html'
            dest_path = os.path.join(dest_dir_path, dest_rel)

            # Ensure destination directory exists (generate_page will also ensure)
            dest_parent = os.path.dirname(dest_path)
            if dest_parent:
                os.makedirs(dest_parent, exist_ok=True)

            generate_page(src_path, template_path, dest_path, basepath=basepath, logger=logger)

