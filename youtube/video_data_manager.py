"""Provides the VideoDataManager class."""


__author__ = "Phixyn"


from youtube.data_classes.video import Video


class VideoDataManager:
    """Holds a dictionary for Video objects and provides methods to interact with
    the dictionary and output video data in different ways.

    Attributes:
        _videos: A dictionary of 'video_id: Video' entries.
    """
    def __init__(self):
        """Initializes an empty dictionary to store Video objects."""
        self._videos = {}

    def add_video(
        self,
        video_id,
        thumbnail_url,
        title,
        length,
        channel,
        channel_url,
        channel_thumbnail_url,
        uploaded_on,
        view_count_text
    ):
        """Constructs a new Video object and adds it to the videos dict. If the video
        is already present in the dict, it is not added again.

        Args:
            video_id: A unique string ID for the video.
            thumbnail_url: URL of the video's thumbnail.
            title: Title of the video.
            length: Length of the video.
            channel: Name of the channel that uploaded the video.
            channel_url: URL of the uploader's channel.
            channel_thumbnail_url: URL of the avatar of the uploader's channel.
            uploaded_on: A string specifying when the video was uploaded.
            view_count_text: A string with the number of views for the video.
        """
        if video_id in self._videos:
            print(f"Video '{video_id}' already in dict, not adding.")
        else:
            self._videos[video_id] = Video(
                video_id,
                f"https://www.youtube.com/watch?v={video_id}",
                thumbnail_url,
                title,
                length,
                channel,
                channel_url,
                channel_thumbnail_url,
                uploaded_on,
                view_count_text
            )

    def add_video_data_object(self, video):
        """Adds a new Video object to the videos dict, if it is not already present
        in the dict.

        Args:
            video: An instance of the Video dataclass, to be added to the dict of
                videos.
        """
        video_id = video.video_id
        if video_id in self._videos:
            print(f"Video '{video_id}' already in dict, not adding.")
        else:
            self._videos[video_id] = video

    def add_videos(self, videos):
        """Adds the given Video objects to the videos dict.

        Args:
            videos: An iterable sequence or set containing Video objects.
        """
        for video in videos:
            self.add_video_data_object(video)

    def get_video(self, video_id):
        """Checks the videos dict for a Video object with the given video ID and returns it.

        Args:
            video_id: The ID of a video to search for in the dict. For example, "dQw4w9WgXcQ".

        Returns:
            A Video object for the given video_id, if it can be found in the dict. If it's not
                found in dict, returns None.
        """
        try:
            return self._videos[video_id]
        except KeyError as e:
            print(f"No video with ID '{video_id}' found in search results.")
            print(e)  # TODO replace with logger, exec_info
            return None

    def get_videos(self):
        """Gets each Video data object in the videos dict.

        Notes:
            Untested method.

        Returns:
            A dictview containing Video data objects present in the videos dict.

        See also:
            https://docs.python.org/3/library/stdtypes.html#dict-views
        """
        return self._videos.values()

    def print_videos(self):
        """Outputs a friendly string representation for each Video object in the
        dict to STDOUT.
        """
        index = 1
        for video in self._videos.values():
            print(f"{index}. {video}")
            index += 1

    def write_videos_to_markdown_file(self, filename="yt_search_results.md"):
        """Produces a nicely formatted Markdown file containing details about
        each Video object in the dict.

        Args:
            filename: The name or path of the file to save to.
        """
        markdown_contents = ["# Search Results Summary\n\n"]

        for video in self._videos.values():
            markdown_contents.append(f"![thumbnail preview]({video.thumbnail_url})\n")
            markdown_contents.append(f"[[{video.video_id}] {video.title}]({video.video_url}) ({video.length}) - {video.view_count_text}  ")
            markdown_contents.append(f"![channel thumbnail preview]({video.channel_thumbnail_url}) {video.channel} - uploaded {video.uploaded_on}\n\n- - -\n")

        with open(filename, "w", encoding="utf-8") as md_file:
            md_file.write("\n".join(markdown_contents))