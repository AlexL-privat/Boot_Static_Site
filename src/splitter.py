import re
from textnode import TextNode, TextType

def split_nodes_delimiter(old_nodes, delimiter, text_type):
    new_nodes = []

    for old in old_nodes:
        if old.text_type != TextType.PLAIN:
            new_nodes.append(old)
            continue

        text = old.text
        idx = 0
        delim_len = len(delimiter)

        while idx < len(text):
            start = text.find(delimiter, idx)
            if start == -1:
                # no more delimiters
                if idx < len(text):
                    new_nodes.append(TextNode(text[idx:], TextType.PLAIN))
                break

            # Add plain text before the delimiter
            if start > idx:
                new_nodes.append(TextNode(text[idx:start], TextType.PLAIN))

            # Check for closing delimiter
            end = text.find(delimiter, start + delim_len)
            if end == -1:
                # If delimiter occurs consecutively (empty block)
                if text[start:start + 2*delim_len] == delimiter * 2:
                    end = start + delim_len
                else:
                    raise ValueError(f"Invalid markdown: missing closing '{delimiter}' delimiter")

            # Extract inner text
            inner_text = text[start + delim_len:end]
            if inner_text:
                new_nodes.append(TextNode(inner_text, text_type))

            # Move index past the closing delimiter
            idx = end + delim_len

    return new_nodes


def split_nodes_link(old_nodes):
    """
    Splits TextNodes containing Markdown links into multiple TextNodes.
    Example: "Check   and  " → Text, Link(a,1), Text, Link(b,2)
    """
    new_nodes = []
    link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    for node in old_nodes:
        if node.text_type != TextType.PLAIN:
            new_nodes.append(node)
            continue

        text = node.text
        last_index = 0

        for match in link_pattern.finditer(text):
            start, end = match.span()
            anchor, url = match.groups()

            # Add preceding plain text
            if start > last_index:
                new_nodes.append(TextNode(text[last_index:start], TextType.PLAIN))

            # Add link node
            new_nodes.append(TextNode(anchor, TextType.LINK, url))
            last_index = end

        # Add remaining plain text
        if last_index < len(text):
            new_nodes.append(TextNode(text[last_index:], TextType.PLAIN))

    return new_nodes


def split_nodes_image(old_nodes):
    new_nodes = []

    image_pattern = re.compile(r"!\[([^\]]*?)\]\((.*?)\)")

    for old in old_nodes:
        if old.text_type != TextType.PLAIN:
            new_nodes.append(old)
            continue

        text = old.text
        current_index = 0

        for match in image_pattern.finditer(text):
            start, end = match.span()
            alt_text, url = match.groups()

            # Text before image
            if start > current_index:
                new_nodes.append(TextNode(text[current_index:start], TextType.PLAIN))

            # Image node with empty string (alt text is stored in the URL parameter semantically)
            new_nodes.append(TextNode("", TextType.IMAGE, url))

            current_index = end

        # Remaining text after last image
        if current_index < len(text):
            new_nodes.append(TextNode(text[current_index:], TextType.PLAIN))

    return new_nodes


def text_to_textnodes(text):
    """
    Convert raw text with markdown-like formatting into a list of TextNode objects.
    Handles bold (**), italic (_), code (`), links ([...](...)), and images (![...](...)).
    """
    # Start with a single plain text node
    nodes = [TextNode(text, TextType.PLAIN)]

    # Order matters: code first (so we don't split formatting inside code)
    nodes = split_nodes_delimiter(nodes, "`", TextType.CODE)
    nodes = split_nodes_delimiter(nodes, "**", TextType.BOLD)
    nodes = split_nodes_delimiter(nodes, "_", TextType.ITALIC)

    # Links and images last
    nodes = split_nodes_image(nodes)
    nodes = split_nodes_link(nodes)

    return nodes