from htmlnode import LeafNode, ParentNode
from textnode import TextType, TextNode
from markdown_extract import markdown_to_blocks, block_to_block_type, BlockType
from splitter import text_to_textnodes

def text_node_to_html_node(text_node: TextNode) -> LeafNode:
    if not isinstance(text_node, TextNode):
        raise ValueError("Input must be a TextNode")

    if text_node.text_type == TextType.PLAIN:
        return LeafNode(tag=None, value=text_node.text)

    if text_node.text_type == TextType.BOLD:
        return LeafNode("b", text_node.text)

    if text_node.text_type == TextType.ITALIC:
        return LeafNode("i", text_node.text)

    if text_node.text_type == TextType.CODE:
        return LeafNode("code", text_node.text)

    if text_node.text_type == TextType.LINK:
        if text_node.URL is None:
            raise ValueError("TextNode of type LINK requires a URL")
        return LeafNode("a", text_node.text, props={"href": text_node.URL})

    if text_node.text_type == TextType.IMAGE:
        if text_node.URL is None:
            raise ValueError("TextNode of type IMAGE requires a URL")
        return LeafNode(
            "img",
            " ",
            props={"src": text_node.URL, "alt": text_node.text}
        )

    # ❌ Unknown enum type → raise exception
    raise ValueError(f"Invalid text_type: {text_node.text_type}")


def text_to_children(text):
    """
    Convert a string of inline markdown text into a list of HTMLNode children.
    Handles bold, italic, code, links, and images.
    
    Args:
        text: A string of markdown text
        
    Returns:
        A list of HTMLNode objects representing the inline elements
    """
    text_nodes = text_to_textnodes(text)
    children = []
    for text_node in text_nodes:
        child = text_node_to_html_node(text_node)
        children.append(child)
    return children


def block_to_html_node(block, block_type):
    """
    Convert a single markdown block into an HTMLNode.
    
    Args:
        block: The markdown block text
        block_type: The BlockType of the block
        
    Returns:
        An HTMLNode representing the block
    """
    if block_type == BlockType.HEADING:
        return heading_block_to_html_node(block)
    elif block_type == BlockType.CODE:
        return code_block_to_html_node(block)
    elif block_type == BlockType.QUOTE:
        return quote_block_to_html_node(block)
    elif block_type == BlockType.UNORDERED_LIST:
        return unordered_list_block_to_html_node(block)
    elif block_type == BlockType.ORDERED_LIST:
        return ordered_list_block_to_html_node(block)
    else:  # PARAGRAPH
        return paragraph_block_to_html_node(block)


def heading_block_to_html_node(block):
    """Convert a heading block to an HTMLNode."""
    # Find the number of # characters
    hashes = 0
    for char in block:
        if char == "#":
            hashes += 1
        else:
            break
    
    # Extract heading text (after the # characters and space)
    heading_text = block[hashes + 1:]
    
    # Convert heading text to children
    children = text_to_children(heading_text)
    
    # Create heading tag (h1-h6)
    tag = f"h{hashes}"
    return ParentNode(tag, children)


def code_block_to_html_node(block):
    """Convert a code block to an HTMLNode."""
    # Remove the opening and closing backticks
    code_text = block[3:-3]
    
    # Code blocks don't parse inline markdown, just create a plain text node
    code_leaf = LeafNode("code", code_text)
    
    # Wrap in a pre tag
    return ParentNode("pre", [code_leaf])


def quote_block_to_html_node(block):
    """Convert a quote block to an HTMLNode."""
    # Split by newlines and remove the > from each line
    lines = block.split("\n")
    quote_lines = []
    
    for line in lines:
        # Remove the > and any following space
        if line.startswith("> "):
            quote_lines.append(line[2:])
        elif line.startswith(">"):
            quote_lines.append(line[1:])
    
    # Join the lines back together
    quote_text = "\n".join(quote_lines)
    
    # Convert to children
    children = text_to_children(quote_text)
    
    return ParentNode("blockquote", children)


def unordered_list_block_to_html_node(block):
    """Convert an unordered list block to an HTMLNode."""
    # Split by newlines
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Remove the "- " prefix
        item_text = line[2:]
        
        # Convert to children
        children = text_to_children(item_text)
        
        # Create list item
        list_item = ParentNode("li", children)
        list_items.append(list_item)
    
    return ParentNode("ul", list_items)


def ordered_list_block_to_html_node(block):
    """Convert an ordered list block to an HTMLNode."""
    # Split by newlines
    lines = block.split("\n")
    list_items = []
    
    for line in lines:
        # Find the dot and space, then extract the text after
        dot_index = line.index(". ")
        item_text = line[dot_index + 2:]
        
        # Convert to children
        children = text_to_children(item_text)
        
        # Create list item
        list_item = ParentNode("li", children)
        list_items.append(list_item)
    
    return ParentNode("ol", list_items)


def paragraph_block_to_html_node(block):
    """Convert a paragraph block to an HTMLNode."""
    # Convert to children
    children = text_to_children(block)
    
    return ParentNode("p", children)


def markdown_to_html_node(markdown):
    """
    Convert a full markdown document into a single parent HTMLNode.
    
    Args:
        markdown: A string containing the full markdown document
        
    Returns:
        A ParentNode (div) containing all block nodes as children
    """
    # Split markdown into blocks
    blocks = markdown_to_blocks(markdown)
    
    # Convert each block to an HTMLNode
    children = []
    for block in blocks:
        block_type = block_to_block_type(block)
        block_node = block_to_html_node(block, block_type)
        children.append(block_node)
    
    # Return a parent div containing all block nodes
    return ParentNode("div", children)