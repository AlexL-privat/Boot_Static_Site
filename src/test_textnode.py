import unittest
from textnode import TextNode, TextType

class TestTextNode(unittest.TestCase):
    def test_eq(self):
        node1 = TextNode("text", TextType.BOLD)
        node2 = TextNode("text", TextType.BOLD)
        self.assertEqual(node1, node2)

    def test_eq_negative(self):
        node1 = TextNode("text", TextType.PLAIN)
        node2 = TextNode("different", TextType.PLAIN)
        self.assertNotEqual(node1, node2)

        node3 = TextNode("text", TextType.BOLD)
        self.assertNotEqual(node1, node3)

        node4 = TextNode("text", TextType.PLAIN, url="https://example.com")
        self.assertNotEqual(node1, node4)

        self.assertNotEqual(node1, "not a TextNode")

    def test_repr(self):
        node = TextNode("Hello", TextType.ITALIC, url="https://example.com")
        expected = "TextNode(text='Hello', text_type=TextType.ITALIC, URL='https://example.com')"
        self.assertEqual(repr(node), expected)

if __name__ == "__main__":
    unittest.main()