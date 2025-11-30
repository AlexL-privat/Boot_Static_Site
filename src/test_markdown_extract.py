import unittest
from markdown_extract import extract_markdown_images, extract_markdown_links, markdown_to_blocks, block_to_block_type, BlockType, extract_title


class TestMarkdownExtract(unittest.TestCase):

    # -----------------------------
    # Image extraction tests
    # -----------------------------
    def test_extract_markdown_images_single(self):
        text = "This is text with an ![image](https://i.imgur.com/zjjcJKZ.png)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("image", "https://i.imgur.com/zjjcJKZ.png")], matches)

    def test_extract_markdown_images_multiple(self):
        text = "![img1](url1) text ![img2](url2)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("img1", "url1"), ("img2", "url2")], matches)

    def test_extract_markdown_images_adjacent(self):
        text = "![a](1)![b](2)![c](3)"
        matches = extract_markdown_images(text)
        self.assertListEqual([("a", "1"), ("b", "2"), ("c", "3")], matches)

    def test_extract_markdown_images_none(self):
        text = "No images here"
        matches = extract_markdown_images(text)
        self.assertListEqual([], matches)

    # -----------------------------
    # Link extraction tests
    # -----------------------------
    def test_single_link(self):
        text = "Here is a [link](https://example.com) in text"
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [("link", "https://example.com")])

    def test_multiple_links(self):
        text = "Here is [a](1) , then [b](2) , and finally [c](3) "
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [("a", "1"), ("b", "2"), ("c", "3")])

    def test_adjacent_links(self):
        text = "[first](url1)[second](url2)[third](url3)"
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [("first", "url1"), ("second", "url2"), ("third", "url3")])

    def test_links_with_special_characters(self):
        text = "Check [a-link_123](https://example.com/test?x=1&y=2)"
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [("a-link_123", "https://example.com/test?x=1&y=2")])

    def test_no_links(self):
        text = "There are no links here!"
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [])

    def test_links_ignored_images(self):
        text = "Image ![alt](img.png) and a link [click](url)"
        matches = extract_markdown_links(text)
        self.assertListEqual(matches, [("click", "url")])


class TestMarkdownToBlocks(unittest.TestCase):

    def test_single_block(self):
        markdown = "This is a single block"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["This is a single block"])

    def test_multiple_blocks(self):
        markdown = "Block 1\n\nBlock 2\n\nBlock 3"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Block 1", "Block 2", "Block 3"])

    def test_blocks_with_whitespace(self):
        markdown = "  Block 1  \n\n  Block 2  "
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Block 1", "Block 2"])

    def test_excessive_newlines(self):
        markdown = "Block 1\n\n\n\nBlock 2"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Block 1", "Block 2"])

    def test_empty_blocks_removed(self):
        markdown = "Block 1\n\n\n\n\n\nBlock 2"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Block 1", "Block 2"])

    def test_blocks_with_internal_newlines(self):
        markdown = "Line 1\nLine 2\n\nBlock 2"
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, ["Line 1\nLine 2", "Block 2"])

    def test_example_markdown(self):
        markdown = """# This is a heading

This is a paragraph of text. It has some **bold** and _italic_ words inside of it.

- This is the first list item in a list block
- This is a list item
- This is another list item"""
        blocks = markdown_to_blocks(markdown)
        expected = [
            "# This is a heading",
            "This is a paragraph of text. It has some **bold** and _italic_ words inside of it.",
            "- This is the first list item in a list block\n- This is a list item\n- This is another list item"
        ]
        self.assertEqual(blocks, expected)

    def test_empty_string(self):
        markdown = ""
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [])

    def test_only_whitespace(self):
        markdown = "   \n\n   \n\n   "
        blocks = markdown_to_blocks(markdown)
        self.assertEqual(blocks, [])


class TestBlockToBlockType(unittest.TestCase):

    # -------- Heading Tests --------
    def test_heading_level_1(self):
        block = "# This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_level_2(self):
        block = "## This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_level_6(self):
        block = "###### This is a heading"
        self.assertEqual(block_to_block_type(block), BlockType.HEADING)

    def test_heading_invalid_no_space(self):
        block = "#This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_heading_invalid_too_many_hashes(self):
        block = "####### This is not a heading"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # -------- Code Block Tests --------
    def test_code_block(self):
        block = "```\nprint('hello')\nprint('world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_single_line(self):
        block = "```code```"
        self.assertEqual(block_to_block_type(block), BlockType.CODE)

    def test_code_block_missing_end(self):
        block = "```\nprint('hello')\nprint('world')"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_code_block_missing_start(self):
        block = "print('hello')\nprint('world')\n```"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # -------- Quote Block Tests --------
    def test_quote_single_line(self):
        block = "> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multiple_lines(self):
        block = "> This is a quote\n> This is also a quote"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_multiple_lines_full(self):
        block = "> Line 1\n> Line 2\n> Line 3"
        self.assertEqual(block_to_block_type(block), BlockType.QUOTE)

    def test_quote_missing_symbol_one_line(self):
        block = "> This is a quote\nThis is not a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_not_quote(self):
        block = "This is not a quote\n> This is a quote"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # -------- Unordered List Tests --------
    def test_unordered_list_single_item(self):
        block = "- Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_multiple_items(self):
        block = "- Item 1\n- Item 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.UNORDERED_LIST)

    def test_unordered_list_invalid_no_space(self):
        block = "-Item 1\n- Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_missing_dash_one_line(self):
        block = "- Item 1\nItem 2\n- Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_unordered_list_wrong_format(self):
        block = "* Item 1\n* Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # -------- Ordered List Tests --------
    def test_ordered_list_single_item(self):
        block = "1. Item 1"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_multiple_items(self):
        block = "1. Item 1\n2. Item 2\n3. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_long(self):
        block = "1. Item 1\n2. Item 2\n3. Item 3\n4. Item 4\n5. Item 5"
        self.assertEqual(block_to_block_type(block), BlockType.ORDERED_LIST)

    def test_ordered_list_invalid_no_space(self):
        block = "1.Item 1\n2. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_wrong_number(self):
        block = "1. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_starts_at_2(self):
        block = "2. Item 1\n3. Item 2"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_invalid_order(self):
        block = "1. Item 1\n2. Item 2\n2. Item 3"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_ordered_list_missing_increment(self):
        block = "1. Item 1\n2. Item 2\n4. Item 4"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    # -------- Paragraph Tests --------
    def test_paragraph_plain_text(self):
        block = "This is a paragraph"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_with_formatting(self):
        block = "This is a paragraph with **bold** and _italic_ text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)

    def test_paragraph_multiple_lines(self):
        block = "This is a paragraph\nwith multiple lines\nof text"
        self.assertEqual(block_to_block_type(block), BlockType.PARAGRAPH)


class TestExtractTitle(unittest.TestCase):

    def test_simple_title(self):
        md = "# Hello"
        self.assertEqual(extract_title(md), "Hello")

    def test_title_with_whitespace(self):
        md = "  #  My Title  \nSome text"
        self.assertEqual(extract_title(md), "My Title")

    def test_first_h1_taken(self):
        md = "# First\n# Second\n"
        self.assertEqual(extract_title(md), "First")

    def test_no_h1_raises(self):
        md = "## Not H1\nNo title here"
        with self.assertRaises(ValueError):
            extract_title(md)


if __name__ == "__main__":
    unittest.main()
