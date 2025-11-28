import unittest
from splitter import split_nodes_delimiter, split_nodes_link, split_nodes_image, text_to_textnodes
from textnode import TextNode, TextType


class TestSplitNodesDelimiter(unittest.TestCase):

    def test_code_split(self):
        node = TextNode("This is text with a `code block` word", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("This is text with a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" word", TextType.PLAIN),
        ]

        self.assertEqual(result, expected)

    def test_bold_split(self):
        node = TextNode("Normal **bold text** still normal", TextType.PLAIN)
        result = split_nodes_delimiter([node], "**", TextType.BOLD)

        expected = [
            TextNode("Normal ", TextType.PLAIN),
            TextNode("bold text", TextType.BOLD),
            TextNode(" still normal", TextType.PLAIN),
        ]

        self.assertEqual(result, expected)

    def test_italic_split(self):
        node = TextNode("A _italic word_ in a sentence", TextType.PLAIN)
        result = split_nodes_delimiter([node], "_", TextType.ITALIC)

        expected = [
            TextNode("A ", TextType.PLAIN),
            TextNode("italic word", TextType.ITALIC),
            TextNode(" in a sentence", TextType.PLAIN),
        ]

        self.assertEqual(result, expected)

    def test_multiple_splits(self):
        # Should alternate through several matches
        node = TextNode("A `one` and `two` and `three`", TextType.PLAIN)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("A ", TextType.PLAIN),
            TextNode("one", TextType.CODE),
            TextNode(" and ", TextType.PLAIN),
            TextNode("two", TextType.CODE),
            TextNode(" and ", TextType.PLAIN),
            TextNode("three", TextType.CODE),
        ]

        self.assertEqual(result, expected)

    def test_no_split_needed(self):
        node = TextNode("Nothing to change here", TextType.BOLD)
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        # should remain unchanged
        self.assertEqual(result, [node])

    def test_missing_closing_delimiter(self):
        node = TextNode("Unclosed **bold text", TextType.PLAIN)
        with self.assertRaises(ValueError) as e:
            split_nodes_delimiter([node], "**", TextType.BOLD)

        self.assertIn("missing closing '**'", str(e.exception) or "")

    def test_empty_text_ignored(self):
        node = TextNode("Start `` end", TextType.PLAIN)  # empty code block
        result = split_nodes_delimiter([node], "`", TextType.CODE)

        expected = [
            TextNode("Start ", TextType.PLAIN),
            TextNode(" end", TextType.PLAIN),
        ]

        self.assertEqual(result, expected)


class TestSplitNodesLinksImages(unittest.TestCase):

    def test_split_links_single(self):
        # ⚠️ CORRECTED: Added a markdown link [a](1) to the text
        node = TextNode("Check [a](1) here", TextType.PLAIN)
        result = split_nodes_link([node])
        expected = [
            TextNode("Check ", TextType.PLAIN),
            TextNode("a", TextType.LINK, "1"),
            TextNode(" here", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

    def test_split_links_multiple(self):
        # ⚠️ CORRECTED: Input node now contains the three links separated by spaces.
        node = TextNode("Links [a](1) [b](2) [c](3)", TextType.PLAIN)
        result = split_nodes_link([node])
        expected = [
            TextNode("Links ", TextType.PLAIN),
            TextNode("a", TextType.LINK, "1"),
            TextNode(" ", TextType.PLAIN),
            TextNode("b", TextType.LINK, "2"),
            TextNode(" ", TextType.PLAIN),
            TextNode("c", TextType.LINK, "3"),
        ]
        # The list comprehension ensures the test is complete by comparing the whole result
        self.assertEqual(result, expected)

    def test_split_links_no_links(self):
        node = TextNode("No links here", TextType.PLAIN)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_split_links_with_non_plain_node(self):
        node = TextNode("Hello", TextType.BOLD)
        result = split_nodes_link([node])
        self.assertEqual(result, [node])

    def test_split_images_single(self):
        node = TextNode("Here is an image ![alt](url) end", TextType.PLAIN)
        result = split_nodes_image([node])
        expected = [
            TextNode("Here is an image ", TextType.PLAIN),
            TextNode("", TextType.IMAGE, url="url"),
            TextNode(" end", TextType.PLAIN),
        ]
        self.assertEqual(result, expected)

    def test_split_images_multiple(self):
        # ⚠️ CORRECTED: Added two markdown image syntaxes ![](1) and ![](2) to the text
        node = TextNode("Images ![](1) ![](2)", TextType.PLAIN)
        result = split_nodes_image([node])
        expected = [
            TextNode("Images ", TextType.PLAIN),
            # Note: Markdown for ![] is often parsed as an empty string for the alt-text
            TextNode("", TextType.IMAGE, url="1"),
            TextNode(" ", TextType.PLAIN),
            TextNode("", TextType.IMAGE, url="2"),
        ]
        self.assertEqual(result, expected)

    def test_split_images_no_images(self):
        node = TextNode("No images here", TextType.PLAIN)
        result = split_nodes_image([node])
        self.assertEqual(result, [node])


class TestTextToTextNodes(unittest.TestCase):

    def test_plain_text(self):
        text = "Just some plain text"
        nodes = text_to_textnodes(text)
        expected = [TextNode("Just some plain text", TextType.PLAIN)]
        self.assertEqual(nodes, expected)

    def test_bold_text(self):
        text = "This is **bold** text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("bold", TextType.BOLD),
            TextNode(" text", TextType.PLAIN)
        ]
        self.assertEqual(nodes, expected)

    def test_italic_text(self):
        text = "This is _italic_ text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" text", TextType.PLAIN)
        ]
        self.assertEqual(nodes, expected)

    def test_code_text(self):
        text = "Here is `code` snippet"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Here is ", TextType.PLAIN),
            TextNode("code", TextType.CODE),
            TextNode(" snippet", TextType.PLAIN)
        ]
        self.assertEqual(nodes, expected)

    def test_link_text(self):
        text = "Go to [boot.dev](https://boot.dev)"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Go to ", TextType.PLAIN),
            TextNode("boot.dev", TextType.LINK, "https://boot.dev")
        ]
        self.assertEqual(nodes, expected)

    def test_image_text(self):
        text = "Image here ![alt](https://img.com/x.png) end"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("Image here ", TextType.PLAIN),
            TextNode("", TextType.IMAGE, "https://img.com/x.png"),
            TextNode(" end", TextType.PLAIN)
        ]
        self.assertEqual(nodes, expected)

    def test_combined_text(self):
        text = ("This is **text** with an _italic_ word and a `code block` and an "
                "![obi wan image](https://i.imgur.com/fJRm4Vk.jpeg) and a [link](https://boot.dev)")
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("text", TextType.BOLD),
            TextNode(" with an ", TextType.PLAIN),
            TextNode("italic", TextType.ITALIC),
            TextNode(" word and a ", TextType.PLAIN),
            TextNode("code block", TextType.CODE),
            TextNode(" and an ", TextType.PLAIN),
            TextNode("", TextType.IMAGE, "https://i.imgur.com/fJRm4Vk.jpeg"),
            TextNode(" and a ", TextType.PLAIN),
            TextNode("link", TextType.LINK, "https://boot.dev"),
        ]
        self.assertEqual(nodes, expected)

    def test_nested_markdown_order(self):
    # Nested markdown not supported yet, just test sequential markdown
        text = "This is **bold** and `code` text"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("This is ", TextType.PLAIN),
            TextNode("bold", TextType.BOLD),
            TextNode(" and ", TextType.PLAIN),
            TextNode("code", TextType.CODE),
            TextNode(" text", TextType.PLAIN)
        ]
        self.assertEqual(nodes, expected)

    def test_adjacent_markdown(self):
        # Bold immediately followed by italic
        text = "**bold**_italic_"
        nodes = text_to_textnodes(text)
        expected = [
            TextNode("bold", TextType.BOLD),
            TextNode("italic", TextType.ITALIC)
        ]
        self.assertEqual(nodes, expected)

if __name__ == "__main__":
    unittest.main()