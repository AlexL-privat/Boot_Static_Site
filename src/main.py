from textnode import TextNode,TextType

def main():
    node = TextNode("Click here", TextType.LINK, "https://example.com")
    print(node)


main()