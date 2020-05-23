"""Provides methods to create and perform HTTP requests to webservers.

TODO:
    * Probably needs better module name.
    * Probably needs to be inside a new package.
"""


__author__ = "Phixyn"


import urllib.request
from urllib.error import URLError

from common import user_agents


def get_raw_html(url, mobile_request=False):
    """Makes a simple HTTP GET request to the specified URL and returns the
    raw HTML response, if successful.
    
    Args:
        url: The URL of the webpage to get the HTML from.
        mobile_request: A boolean indicating if the website we're hitting is
            a mobile website. If this is true, the user-agent header for the
            request is set to a mobile browser's UA.

    Returns:
        The response, in bytes, from the urllib request. This contains the
        raw HTML, which can be passed to a HTML parser. If the request fails,
        an error is printed and None is returned.
    """
    user_agent = user_agents.ANDROID_CHROME_APP_USER_AGENT \
        if mobile_request else user_agents.DESKTOP_FIREFOX_USER_AGENT

    # TODO handle POST too?
    http_request = urllib.request.Request(url)
    http_request.add_header("User-Agent", user_agent)
    raw_html = None

    try:
        with urllib.request.urlopen(http_request) as response:
            raw_html = response.read()
    except URLError as e:
        if hasattr(e, "reason"):
            # TODO replace with logger
            print("Failed to reach server.")
            print("Reason: ", e.reason)
        # HTTPError
        elif hasattr(e, "code"):
            print("The server couldn't fullfil the request.")
            print("HTTP error code: ", e.code)

    return raw_html