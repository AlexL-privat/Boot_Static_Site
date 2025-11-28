import unittest
from textnode import TextNode, TextType
from htmlnode import LeafNode, ParentNode
from converter import text_node_to_html_node, markdown_to_html_node  

class TestTextNodeToHTML(unittest.TestCase):

    def test_plain(self):
        node = TextNode("hello", TextType.PLAIN)
        html = text_node_to_html_node(node)
        self.assertEqual(html, LeafNode(None, "hello"))

    def test_bold(self):
        node = TextNode("bold", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.assertEqual(html, LeafNode("b", "bold"))

    def test_italic(self):
        node = TextNode("italic", TextType.ITALIC)
        html = text_node_to_html_node(node)
        self.assertEqual(html, LeafNode("i", "italic"))

    def test_code(self):
        node = TextNode("print(x)", TextType.CODE)
        html = text_node_to_html_node(node)
        self.assertEqual(html, LeafNode("code", "print(x)"))

    def test_link(self):
        node = TextNode("Click", TextType.LINK, url="https://example.com")
        html = text_node_to_html_node(node)
        self.assertEqual(html, LeafNode("a", "Click", props={"href": "https://example.com"}))

    def test_image(self):
        node = TextNode("alt", TextType.IMAGE, url="https://img.com/x.png")
        html = text_node_to_html_node(node)
        self.assertEqual(
            html,
            LeafNode("img", " ", props={"src": "https://img.com/x.png", "alt": "alt"})
        )

    def test_invalid_type(self):
        node = TextNode("x", "BAD_TYPE")  # Not enum
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_image_requires_url(self):
        node = TextNode("alt", TextType.IMAGE)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_link_requires_url(self):
        node = TextNode("Click", TextType.LINK)
        with self.assertRaises(ValueError):
            text_node_to_html_node(node)

    def test_non_textnode_input(self):
        with self.assertRaises(ValueError):
            text_node_to_html_node("not a node")

    def test_repr_output(self):
        node = TextNode("hi", TextType.BOLD)
        html = text_node_to_html_node(node)
        self.assertIn("HTMLNode(tag='b'", repr(html))


class TestMarkdownToHTMLNode(unittest.TestCase):

    def test_heading_single(self):
        markdown = "# This is a heading"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.tag, "div")
        self.assertEqual(len(html.children), 1)
        self.assertEqual(html.children[0].tag, "h1")

    def test_heading_multiple_levels(self):
        markdown = "# H1\n\n## H2\n\n### H3"
        html = markdown_to_html_node(markdown)
        self.assertEqual(len(html.children), 3)
        self.assertEqual(html.children[0].tag, "h1")
        self.assertEqual(html.children[1].tag, "h2")
        self.assertEqual(html.children[2].tag, "h3")

    def test_paragraph_single(self):
        markdown = "This is a simple paragraph."
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.tag, "div")
        self.assertEqual(len(html.children), 1)
        self.assertEqual(html.children[0].tag, "p")

    def test_paragraph_with_formatting(self):
        markdown = "This is a **bold** word and an _italic_ word."
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.children[0].tag, "p")
        # Check that children include bold and italic nodes
        p_children = html.children[0].children
        # Should have multiple children due to formatting
        self.assertGreater(len(p_children), 1)

    def test_code_block(self):
        markdown = "```\nprint('hello')\nprint('world')\n```"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.tag, "div")
        self.assertEqual(len(html.children), 1)
        self.assertEqual(html.children[0].tag, "pre")
        self.assertEqual(html.children[0].children[0].tag, "code")

    def test_code_block_no_markdown_parsing(self):
        markdown = "```\nprint(**bold**)\nprint(_italic_)\n```"
        html = markdown_to_html_node(markdown)
        code_content = html.children[0].children[0].value
        # Code content should NOT have parsed markdown
        self.assertIn("**bold**", code_content)
        self.assertIn("_italic_", code_content)

    def test_quote_block_single(self):
        markdown = "> This is a quote"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.children[0].tag, "blockquote")

    def test_quote_block_multiple_lines(self):
        markdown = "> Line 1\n> Line 2\n> Line 3"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.children[0].tag, "blockquote")

    def test_unordered_list(self):
        markdown = "- Item 1\n- Item 2\n- Item 3"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.children[0].tag, "ul")
        self.assertEqual(len(html.children[0].children), 3)
        self.assertEqual(html.children[0].children[0].tag, "li")

    def test_unordered_list_with_formatting(self):
        markdown = "- **Bold** item\n- _Italic_ item"
        html = markdown_to_html_node(markdown)
        ul = html.children[0]
        self.assertEqual(ul.tag, "ul")
        # Each list item should have children for inline formatting
        self.assertGreater(len(ul.children[0].children), 1)

    def test_ordered_list(self):
        markdown = "1. First\n2. Second\n3. Third"
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.children[0].tag, "ol")
        self.assertEqual(len(html.children[0].children), 3)
        self.assertEqual(html.children[0].children[0].tag, "li")

    def test_ordered_list_with_formatting(self):
        markdown = "1. **First** item\n2. _Second_ item"
        html = markdown_to_html_node(markdown)
        ol = html.children[0]
        self.assertEqual(ol.tag, "ol")
        self.assertGreater(len(ol.children[0].children), 1)

    def test_mixed_blocks(self):
        markdown = """# Heading

This is a paragraph.

- List item 1
- List item 2

> A quote

```
code
```"""
        html = markdown_to_html_node(markdown)
        # Should have 5 block children
        self.assertEqual(len(html.children), 5)
        self.assertEqual(html.children[0].tag, "h1")
        self.assertEqual(html.children[1].tag, "p")
        self.assertEqual(html.children[2].tag, "ul")
        self.assertEqual(html.children[3].tag, "blockquote")
        self.assertEqual(html.children[4].tag, "pre")

    def test_empty_markdown(self):
        markdown = ""
        html = markdown_to_html_node(markdown)
        self.assertEqual(html.tag, "div")
        self.assertEqual(len(html.children), 0)

    def test_heading_with_inline_markdown(self):
        markdown = "# Heading with **bold** and _italic_"
        html = markdown_to_html_node(markdown)
        h1 = html.children[0]
        self.assertEqual(h1.tag, "h1")
        # Should have multiple children for inline formatting
        self.assertGreater(len(h1.children), 1)

    def test_paragraph_with_link(self):
        markdown = "Check out [my website](https://example.com) for more."
        html = markdown_to_html_node(markdown)
        p = html.children[0]
        self.assertEqual(p.tag, "p")
        # Should have children including a link node
        has_link = False
        for child in p.children:
            if hasattr(child, 'tag') and child.tag == "a":
                has_link = True
                break
        self.assertTrue(has_link)

    def test_paragraph_with_image(self):
        markdown = "Here is an image ![alt text](https://img.com/pic.png)"
        html = markdown_to_html_node(markdown)
        p = html.children[0]
        self.assertEqual(p.tag, "p")
        # Should have children including an image node
        has_image = False
        for child in p.children:
            if hasattr(child, 'tag') and child.tag == "img":
                has_image = True
                break
        self.assertTrue(has_image)

    def test_complex_document(self):
        markdown = """# My Document

This is a paragraph with **bold** and _italic_ text.

## Subsection

Here is a [link](https://example.com) and an ![image](https://img.com/pic.png).

- First item with **bold**
- Second item
- Third item

> A quote with _emphasis_

```
def hello():
    print("world")
```

Final paragraph."""
        html = markdown_to_html_node(markdown)
        # Should be a div with multiple children
        self.assertEqual(html.tag, "div")
        self.assertGreater(len(html.children), 1)
        # First child should be h1
        self.assertEqual(html.children[0].tag, "h1")

    def test_to_html_output(self):
        markdown = "# Hello"
        html = markdown_to_html_node(markdown)
        html_string = html.to_html()
        # Should produce valid HTML
        self.assertIn("<div>", html_string)
        self.assertIn("<h1>", html_string)
        self.assertIn("Hello", html_string)
        self.assertIn("</h1>", html_string)
        self.assertIn("</div>", html_string)

if __name__ == "__main__":
    unittest.main()