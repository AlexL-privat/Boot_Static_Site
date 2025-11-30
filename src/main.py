import sys

from textnode import TextNode, TextType
from fs_utils import copy_dir_recursive
from generator import generate_pages_recursive


def main():
    # small demo object still printed for backwards compatibility
    node = TextNode("Click here", TextType.LINK, "https://example.com")
    print(node)

    # Perform a site copy from `static` -> `docs` by default.
    try:
        copy_dir_recursive("static", "docs")
    except Exception as e:
        print(f"Error copying static files: {e}")

    # Determine basepath from CLI first argument (default "/")
    basepath = sys.argv[1] if len(sys.argv) > 1 else '/'

    # Generate HTML pages for every markdown file in `content` -> `docs`
    try:
        generate_pages_recursive("content", "template.html", "docs", basepath=basepath)
    except Exception as e:
        print(f"Error generating pages: {e}")


if __name__ == "__main__":
    main()