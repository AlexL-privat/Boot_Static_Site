from textnode import TextNode, TextType
from fs_utils import copy_dir_recursive
from generator import generate_pages_recursive


def main():
    # small demo object still printed for backwards compatibility
    node = TextNode("Click here", TextType.LINK, "https://example.com")
    print(node)

    # Perform a site copy from `static` -> `public` by default.
    try:
        copy_dir_recursive("static", "public")
    except Exception as e:
        print(f"Error copying static files: {e}")

    # Generate HTML pages for every markdown file in `content` -> `public`
    try:
        generate_pages_recursive("content", "template.html", "public")
    except Exception as e:
        print(f"Error generating pages: {e}")


if __name__ == "__main__":
    main()