"""Provides methods to process HTML strings using BeautifulSoup4.

TODO:
    * Probably needs better module name
    * Probably needs to be inside a new package
"""


__author__ = "Phixyn"


from bs4 import BeautifulSoup


def make_soup(html):
    """Initializes a BeautifulSoup object using the given HTML string.

    Args:
        html: A string containing HTML for parsing.

    Returns:
        A BeautifulSoup object initialized with the HTML string.
    """
    # Debug - Write HTML to file
    with open("debug_soup.html", "wb") as fob:
        fob.write(html)

    return BeautifulSoup(html, "lxml")