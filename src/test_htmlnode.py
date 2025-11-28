import unittest
from htmlnode import HTMLNode, LeafNode, ParentNode  # adjust if your filename differs


class TestHTMLNode(unittest.TestCase):

    def test_props_to_html_empty(self):
        node = HTMLNode()
        self.assertEqual(node.props_to_html(), "")

    def test_props_to_html_single(self):
        node = HTMLNode(props={"href": "https://example.com"})
        self.assertEqual(node.props_to_html(), ' href="https://example.com"')

    def test_props_to_html_multiple(self):
        node = HTMLNode(props={"class": "btn", "id": "main"})
        result = node.props_to_html()
        # Order in dicts is preserved in Python 3.7+, so this is safe:
        self.assertEqual(result, ' class="btn" id="main"')

    def test_repr(self):
        node = HTMLNode(
            tag="a",
            value="Click",
            children=[HTMLNode(tag="span", value="inner")],
            props={"href": "https://example.com"}
        )
        expected = (
            "HTMLNode(tag='a', value='Click', "
            "children=[HTMLNode(tag='span', value='inner', children=[], props={})], "
            "props={'href': 'https://example.com'})"
        )
        self.assertEqual(repr(node), expected)

    def test_to_html_not_implemented(self):
        node = HTMLNode()
        with self.assertRaises(NotImplementedError):
            node.to_html()


class TestLeafNode(unittest.TestCase):

    def test_no_children_allowed(self):
        node = LeafNode("p", "hello")
        self.assertEqual(node.children, [])

    def test_constructor_requires_value(self):
        with self.assertRaises(ValueError):
            LeafNode("p", None)

    def test_to_html_raises_on_empty_value(self):
        node = LeafNode("p", "hello")
        node.value = ""  # force empty
        with self.assertRaises(ValueError):
            node.to_html()

    def test_to_html_raw_text_if_no_tag(self):
        node = LeafNode(None, "raw text")
        self.assertEqual(node.to_html(), "raw text")

    def test_to_html_single_prop(self):
        node = LeafNode("a", "Click", props={"href": "https://example.com"})
        self.assertEqual(node.to_html(), '<a href="https://example.com">Click</a>')

    def test_to_html_multiple_props(self):
        node = LeafNode("div", "Box", props={"class": "card", "id": "top"})
        self.assertEqual(node.to_html(), '<div class="card" id="top">Box</div>')

    def test_to_html_tag_render(self):
        node = LeafNode("b", "Bold")
        self.assertEqual(node.to_html(), "<b>Bold</b>")

    def test_to_html_falsy_nonempty_value(self):
        # numeric 0 or "False" are valid values but should still render
        node = LeafNode("span", "0")
        self.assertEqual(node.to_html(), "<span>0</span>")

    def test_repr_with_tag(self):
        node = LeafNode("span", "hi", props={"x": "1"})
        self.assertEqual(
            repr(node),
            "HTMLNode(tag='span', value='hi', children=[], props={'x': '1'})"
        )


class TestParentNode(unittest.TestCase):

    def test_constructor_requires_children(self):
        # children required → leaving it out must error
        with self.assertRaises(TypeError):
            ParentNode("div")

    def test_constructor_requires_tag(self):
        with self.assertRaises(TypeError):
            ParentNode(children=[LeafNode("span", "x")])  # no tag positional arg

    def test_to_html_no_tag(self):
        node = ParentNode("div", [LeafNode("span", "x")])
        node.tag = None  # force invalid
        with self.assertRaises(ValueError) as e:
            node.to_html()
        self.assertEqual(str(e.exception), "ParentNode requires a tag")

    def test_to_html_missing_children_none(self):
        node = ParentNode("div", [LeafNode("span", "x")])
        node.children = None  # simulate missing
        with self.assertRaises(ValueError) as e:
            node.to_html()
        self.assertEqual(str(e.exception), "ParentNode requires children (missing children)")

    def test_to_html_missing_children_empty_list(self):
        node = ParentNode("div", [])
        with self.assertRaises(ValueError) as e:
            node.to_html()
        self.assertEqual(str(e.exception), "ParentNode requires children, but child list is empty")

    def test_to_html_recursive_render(self):
        child1 = LeafNode("b", "1")
        child2 = LeafNode("i", "2")
        parent = ParentNode("p", [child1, child2])
        self.assertEqual(parent.to_html(), "<p><b>1</b><i>2</i></p>")

    def test_to_html_nested_recursive_render(self):
        # structure: <div><p><b>x</b></p><i>y</i></div>
        inner = ParentNode("p", [LeafNode("b", "x")])
        outer = ParentNode("div", [inner, LeafNode("i", "y")])
        self.assertEqual(outer.to_html(), "<div><p><b>x</b></p><i>y</i></div>")

    def test_children_must_be_htmlnode(self):
        node = ParentNode("div", ["not a node"])
        with self.assertRaises(ValueError):
            node.to_html()

    def test_repr(self):
        node = ParentNode("section", [LeafNode("p", "hi")], props={"id": "1"})
        self.assertEqual(
            repr(node),
            "HTMLNode(tag='section', value=None, children=[HTMLNode(tag='p', value='hi', children=[], props={})], props={'id': '1'})"
        )


if __name__ == "__main__":
    unittest.main()