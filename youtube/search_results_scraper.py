"""YouTube search results scraper concept.
Based on url_markify.py and preview_scraper.py

Does not use the YouTube/Google API.
"""


__author__ = "Phixyn"
__version__ = "1.0.0"


import json
import re
import sys

from common import http_handler
from common import soup_handler
from youtube.search_results_json_parser import SearchResultsJSONParser
from youtube.video_data_manager import VideoDataManager


def get_results_json(soup):
    """Process a BS4 object to get a JSON object containing search result data.

    Seems like each search result page comes with a JavaScript object
    containing all information about each video in the results.
    It then has placeholder HTML elements for each result, but these
    are empty and they are populated somehow using JavaScript (this
    can also be seen in a normal browser).

    Because of this, we need to use the JavaScript object (we can parse
    it as JSON) to get our search results. This is a nicer approach
    anyway, so I think YouTube accidentally gave scrapers an easy way
    to scrape results by trying to make our lives harder.

    Args:
        soup: A BeautifulSoup (BS4) object.

    Returns:
        A JSON object containing data from the YouTube search results.
    """
    soup_yt_initial_data_regex = "window\[\"ytInitialData\"\]\ \="
    # Get the text inside the script element containing our JavaScript object/JSON
    # TL;DR this is the script element that contains the JavaScript object
    # we want to parse.
    unparsed_soup_text = soup.find("script", text=re.compile(soup_yt_initial_data_regex)).string

    # Find where the ytInitialData variable ends and ytInitialPlayerResponse starts
    yt_initial_data_js_var_string = "window[\"ytInitialData\"] ="
    
    yt_initial_data_js_var_start_index = unparsed_soup_text.find(yt_initial_data_js_var_string) + len(yt_initial_data_js_var_string)
    yt_initial_data_js_var_end_index = unparsed_soup_text.find("window[\"ytInitialPlayerResponse\"] =")
    # Extract just the JSON value from the script element's text
    parsed_soup_text = unparsed_soup_text[yt_initial_data_js_var_start_index:yt_initial_data_js_var_end_index].strip("\n\r; ")

    # For debugging: write to file
    with open("yt_scraper_json_debug.json", "wb") as fob:
        fob.write(parsed_soup_text.encode("utf-8"))

    # Deserialize JSON string to a Python dict
    results_json = json.loads(parsed_soup_text.encode("utf-8"))
    return results_json


def get_results_json_for_mobile(soup):
    """Process a BS4 object to get a JSON object containing search result data.

    Like the method above, this returns a JSON object containing data
    from the YouTube search results. However, it uses the HTML response
    from the mobile version of the website. This HTML is actually much
    nicer to work with, because the initial data variable (i.e. the
    variable that holds the JSON we want) is in a single comment
    inside a single div element.

    This means we don't have to use RegEx or .find() or any kinds
    of crazy stuff to get the JSON. All we need is the string attribute
    of the div element's BS4 tag object. God bless mobile peasants for
    once being helpful to us hackers ;)

    Args:
        soup: A BeautifulSoup (BS4) object.

    Returns:
        A JSON object containing data from the YouTube search results.
    """
    parsed_soup_text = soup.find("div", id="initial-data").string.strip()
    # Look at how much nicer and simpler it is! Literally 2 lines.

    # For debugging: write to file
    with open("yt_scraper_json_debug.json", "wb") as fob:
        fob.write(parsed_soup_text.encode("utf-8"))

    # Deserialize JSON string to a Python dict
    results_json = json.loads(parsed_soup_text.encode("utf-8"))
    return results_json


def get_json_for_search(query,
                        continuation_token=None,
                        clicking_param_token=None,
                        sort_by_recent=True,
                        use_mobile=True):
    """Performs a YouTube search using the given query string and
    returns a JSON object with data from the search results.
    
    Usage examples:
        get_json_for_search("python")
        Equivalent to a search URL containing:
        https://www.youtube.com/results?search_query=python&sp=CAI%253D

        get_json_for_search("hello+world")
        Equivalent to a search URL containing:
        https://www.youtube.com/results?search_query=hello+world&sp=CAI%253D

        Note: '+' denotes a space

    Args:
        query: A YouTube search query string. To see an example, perform a
            search on YouTube and look at the URL. The query string will be
            after 'search_query='.
        continuation_token: A token used in a URL that requests more search
            results from the server. In the client, the page is an infinite
            scrolling page, and more results are loaded when the user scrolls
            to the bottom of the page. As a scraper, we can't scroll, so we
            need to hit the 'continuation URL' with this token. This token
            is found in the search results JSON response.
        clicking_param_token: Another token needed for the continuation URL,
            also included in the search results JSON response.
        sort_by_recent: A boolean indicating whether the YouTube search should
            be performed using the upload date filter. This filter returns the
            most recently uploaded videos in the search result.
        use_mobile: A boolean indicating whether the mobile version of the
            YouTube website should be used to perform the search. Generally,
            this is recommended because the response HTML is much nicer to work
            with and faster to parse (see get_results_json_for_mobile() for
            explanation).
    
    Returns:
        A JSON object containing data from the search results.
    """
    base_url = "https://m.youtube.com/results" \
        if use_mobile else "https://www.youtube.com/results"
    search_query_param = f"search_query={query}"
    # Filter by upload date (newest) (this also works on mobile, even though
    # the mobile website/app don't have a UI for this functionality).
    # TODO use sort_by_recent to decide if this should be included in search URL
    #   (maybe just append to end of search_url as needed)
    filter_by_upload_date_param = "sp=CAI%253D"
    ctoken_param = f"ctoken={continuation_token}"
    continuation_param = f"continuation={continuation_token}"
    itct_param = f"itct={clicking_param_token}"

    if continuation_token and clicking_param_token:
        search_url = f"{base_url}?{'&'.join((search_query_param, filter_by_upload_date_param, ctoken_param, continuation_param, itct_param))}"
    else:
        search_url = f"{base_url}?{'&'.join((search_query_param, filter_by_upload_date_param))}"

    # HTTP GET request for search URL
    print(f"Performing search using URL: '{search_url}'")
    raw_html = http_handler.get_raw_html(search_url, mobile_request=use_mobile)
    if not raw_html:
        # TODO: Replace print with logging
        print("Error getting raw HTML.")
        sys.exit(1)

    # BeautifulSoup object
    soup = soup_handler.make_soup(raw_html)

    # Parse HTML using BeautifulSoup
    results_json = get_results_json_for_mobile(soup) \
        if use_mobile else get_results_json(soup)

    return results_json


if __name__ == "__main__":
    video_data_manager = VideoDataManager()

    search_query = "python"
    # results_json = get_json_for_search(search_query, use_mobile=False)
    mobile_results_json = get_json_for_search(search_query)

    # results_parser = SearchResultsJSONParser(mobile_results_json)
    results_parser = SearchResultsJSONParser()
    results_parser.parse_video_results(mobile_results_json)
    # Debug - write JSON response to file
    results_parser.write_results_json_to_file()
    # TODO testing multiple calls to make sure there's no duplicates,
    # but in real usage only need to call at the end.
    video_data_manager.add_videos(results_parser.get_video_results())

    estimated_results = results_parser.get_estimated_results_count()
    print(f"Search found {estimated_results} results.")
    if estimated_results == 0:
        print(f"No results found for: {search_query}")
        sys.exit(0)

    # "Round 2" of results. Mostly for testing. Proper infinite scrolling
    # handling needs to take place, wherein user can specify how many
    # results they want to store. We also probably need some sort of
    # flood control mechanism.
    if estimated_results > 0:
        # In the future we should also check if estimated_results > desired_results
        ctoken, ctp = results_parser.get_next_continuation_data()
        if not ctoken is None or not ctp is None:
            # we probably want to log these at debug level
            # print(f"Continuation Token: {token}")
            # print(f"CTP: {ctp}")
            # results_parser.parse_video_results(get_json_for_search(search_query, ctoken, ctp))
            results_parser.parse_video_results(get_json_for_search(search_query, ctoken, ctp))
            # Debug - write JSON response to file
            results_parser.write_results_json_to_file(filename="continuations_json.json")

            # TODO see above usage, this can be called at the end. This is just here for testing.
            video_data_manager.add_videos(results_parser.get_video_results())

    # Parse video data from results and output them
    video_data_manager.print_videos()
    video_data_manager.write_videos_to_markdown_file()

    #
    # TODO Infinite scroll handling
    # estimated_results = results_parser.get_estimated_results_count()
    # while estimated_results < videos we have:
    #   ctoken, ctp = results_parser.get_next_continuation_data()
    #
    #   results_parser.update_results_json(get_json_for_search(search_query, ctoken, ctp))
    #   need to check if json contains anything that tells us there's
    #       no more results
    #   parse all results at once, or let user specify limit of how many
    #       results we get