"""Provides the SearchResultsJSONParser class."""


__author__ = "Phixyn"


import json
from youtube.data_classes.video import Video


class SearchResultsJSONParser:
    """Implements methods used to parse and perform operations on the
    JSON response received for YouTube search results.

    Attributes:
        _json: A JSON object received from the YouTube servers containing
            data about a particular search's results.
        _videos: A list of Video data objects constructed from the parsed
            search results.

    Notes:
        Only supports the mobile JSON response right now.
    """
    def __init__(self, results_json=None):
        """Initializes SearchResultsJSONParser. If a results JSON is passed to
        this constructor, the method parse_video_results() is called.

        Args:
            results_json: A JSON object obtained from the response of a YouTube
                search. Typically this is found in the HTML response inside a
                script tag of the HTML with the variable 'ytInitialData'. On
                the mobile version, it is found inside a div tag with the ID
                'initial-data'.
        """
        self._json = results_json
        self._videos = []

        if self._json is not None:
            self.parse_video_results(self._json)

    def _gen_dict_extract(self, key, var):
        """Generator function which yields all occurrences of a given key in a
        nested map or sequence, such as a dict or a list. The map or sequence
        is traversed using recursion. Each occurrence found is yielded to
        return a generator iterator.

        Args:
            key: The key to search for in the nested data structure.
            var: The nested data structure.

        Returns:
            A generator iterator which can be used to retrieve all the
            occurrences of the given key in the given map or sequence.
            As an example, the returned iterator can be used to retrieve
            values nested deep within a dictionary representing a JSON object.

        See also:
            Source: https://stackoverflow.com/a/29652561, modified to work in
            Python 3.
        """
        # Check if the given object has an items() function, in case strings
        # are passed during recursion.
        if hasattr(var, 'items'):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, dict):
                    # Note: mind this call if method is moved outside a class
                    for result in self._gen_dict_extract(key, v):
                        yield result
                elif isinstance(v, list):
                    for d in v:
                        for result in self._gen_dict_extract(key, d):
                            yield result

    def parse_video_results(self, results_json):
        """Parses the JSON received for a YouTube search and extracts video
        data from it. Populates the videos list with Video objects constructed
        with the extracted data.

        Args:
            results_json: A JSON object obtained from the response of a YouTube
                search. Typically this is found in the HTML response inside a
                script tag of the HTML with the variable 'ytInitialData'. On
                the mobile version, it is found inside a div tag with the ID
                'initial-data'.
        """
        # Can't just use
        # results_json["contents"]["sectionListRenderer"]["contents"][0]["itemSectionRenderer"]["contents"]
        # because results_json["contents"]["sectionListRenderer"]["contents"][0] may have a
        # "promotedSparklesTextSearchRenderer" instead of a "itemSectionRenderer", for ads/sponsored results
        # Note: _gen_dict_extract is a generator
        self._json = results_json
        video_data = self._gen_dict_extract("compactVideoRenderer", self._json)

        for video in video_data:
            video_id = video["videoId"]
            try:
                self._videos.append(
                    Video(
                        video_id,
                        f"https://www.youtube.com/watch?v={video_id}",
                        video["thumbnail"]["thumbnails"][0]["url"],
                        video["title"]["runs"][0]["text"],
                        video["lengthText"]["runs"][0]["text"],
                        video["longBylineText"]["runs"][0]["text"],
                        video["longBylineText"]["runs"][0]["navigationEndpoint"]["commandMetadata"]["webCommandMetadata"]["url"],
                        video["channelThumbnail"]["thumbnails"][0]["url"],
                        video["publishedTimeText"]["runs"][0]["text"],
                        video["viewCountText"]["runs"][0]["text"]
                    )
                )
            except KeyError as e:
                # TODO somehow handle creating an instance of Video with the
                # data we can get, so that one or two KeyErrors don't prevent
                # us from storing the rest of the video's data.
                print(f"KeyError for video with ID {video_id}.")
                print(e)

    def get_estimated_results_count(self):
        """Gets the number of estimated video results found for the
        YouTube search.

        Returns:
            Number of estimated search results.
        """
        return int(self._json["estimatedResults"])

    def get_video_results(self):
        """Gets a list of video data objects.

        Returns:
            A list of video data objects constructed from the parsed
            search results.
        """
        return self._videos

    def get_next_continuation_data(self):
        """Extracts data necessary to form a 'continuation URL' used to load
        more search results.

        In the client, the page is an infinite scrolling page, and more results
        are loaded when the user scrolls to the bottom of the page. As a
        scraper, we can't scroll, so we need to hit the 'continuation URL' with
        some data in it. This data can be extracted from the 'continuations'
        and 'nextContinuationData' properties of the search results' JSON.

        Returns:
            A tuple containing a continuation token and a clicking param token.
            Both of these tokens are needed to construct a 'continuation URL'
            used to request more search results from the server.
        """
        continuation_data_generator = self._gen_dict_extract("nextContinuationData", self._json)
        continuation_data = None

        it = iter(continuation_data_generator)
        try:
            continuation_data = next(it)
            return (continuation_data['continuation'], continuation_data['clickTrackingParams'])
        except StopIteration as e:
            print("Error: Could not get continuation data.")
            print(e)
            return None
        except KeyError as e:
            print("Error: Could not get continuation data.")
            print(e)
            return None

    def print_results_json(self):
        """Outputs the search results' JSON to STDOUT."""
        print(self._json)

    def write_results_json_to_file(self, filename="debug_result_json.json"):
        """Writes the search results' JSON to a file.

        Args:
            filename: The name or path of the file to save to.
        """
        with open(filename, "w") as fob:
            json.dump(self._json, fob, indent=4)