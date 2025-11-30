import re
from enum import Enum


class BlockType(Enum):
    HEADING = "heading"
    CODE = "code"
    QUOTE = "quote"
    UNORDERED_LIST = "unordered_list"
    ORDERED_LIST = "ordered_list"
    PARAGRAPH = "paragraph"

def extract_markdown_images(text):
    # ![alt](url)
    pattern = r"!\[(.*?)\]\((.*?)\)"
    return re.findall(pattern, text)


def extract_markdown_links(text):
    """
    Extract markdown links [text](url) but ignore images ![alt](url)
    Returns list of (text, url) tuples
    """
    # Pattern explanation:
    # (?<!\!)        -> negative lookbehind, ensures not preceded by '!'
    # \[([^\]]*?)\]  -> match link text inside brackets (non-greedy)
    # \((.*?)\)      -> match URL inside parentheses (non-greedy)
    pattern = r'(?<!\!)\[([^\]]*?)\]\((.*?)\)'
    return re.findall(pattern, text)


def markdown_to_blocks(markdown):
    """
    Split a markdown document into blocks separated by double newlines.
    
    Each block is stripped of leading/trailing whitespace.
    Empty blocks (from excessive newlines) are removed.
    
    Args:
        markdown: A string containing the full markdown document
        
    Returns:
        A list of block strings
    """
    blocks = markdown.split("\n\n")
    result = []
    
    for block in blocks:
        stripped = block.strip()
        if stripped:  # Only add non-empty blocks
            result.append(stripped)
    
    return result


def block_to_block_type(block):
    """
    Determine the type of a markdown block.
    
    Args:
        block: A single block of markdown text (whitespace already stripped)
        
    Returns:
        A BlockType enum value representing the block type
    """
    lines = block.split("\n")
    
    # Check for heading (1-6 # followed by space)
    if block.startswith("#"):
        hashes = 0
        for char in block:
            if char == "#":
                hashes += 1
            else:
                break
        if 1 <= hashes <= 6 and len(block) > hashes and block[hashes] == " ":
            return BlockType.HEADING
    
    # Check for code block (starts and ends with 3 backticks)
    if block.startswith("```") and block.endswith("```"):
        return BlockType.CODE
    
    # Check for quote block (every line starts with >)
    is_quote = True
    for line in lines:
        if not line.startswith(">"):
            is_quote = False
            break
    if is_quote:
        return BlockType.QUOTE
    
    # Check for unordered list (every line starts with - followed by space)
    is_unordered = True
    for line in lines:
        if not line.startswith("- "):
            is_unordered = False
            break
    if is_unordered:
        return BlockType.UNORDERED_LIST
    
    # Check for ordered list (lines start with number, dot, space - incrementing)
    is_ordered = True
    for i, line in enumerate(lines, 1):
        expected_prefix = f"{i}. "
        if not line.startswith(expected_prefix):
            is_ordered = False
            break
    if is_ordered:
        return BlockType.ORDERED_LIST
    
    # Default to paragraph
    return BlockType.PARAGRAPH


def extract_title(markdown: str) -> str:
    """
    Extract the first H1 title (a line that starts with a single '# ')

    Args:
        markdown: Full markdown document string

    Returns:
        The title text with the leading '#' and surrounding whitespace removed

    Raises:
        ValueError: if no H1 title is found
    """
    for line in markdown.splitlines():
        stripped = line.strip()
        if stripped.startswith('# '):
            return stripped[2:].strip()

    raise ValueError("No H1 title found in markdown")
