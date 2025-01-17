import re

def clean_text(text):
    """
    Clean the text by removing spaces before punctuation marks (dots, commas, etc.)
    and strip any leading or trailing whitespace.

    Args:
        text (str): The text to clean

    Returns:
        str: The cleaned text
    """
    if text:
        return re.sub(r'\s([.,!?;:])', r'\1', text).strip()
    
    return ""


def get_text_with_spaces(tag):
    """
    Get the text content of a tag, recursively joining all its stripped strings, adding spaces between them.

    Args:
        tag (bs4.element.Tag): The tag to get the text from

    Returns:
        str: The cleaned text
    """
    if tag:
        return clean_text(' '.join(tag.stripped_strings))
    
    return ""