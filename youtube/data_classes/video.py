"""Provides the Video dataclass."""


__author__ = "Phixyn"


from dataclasses import dataclass


@dataclass
class Video:
    """Holds data pertaining to a YouTube video.

    TODO: make some of these optional so that if we can't get
          all properties, we can still make an instance of this
          (e.g. uploaded_on is sometimes not present for "Topic
          channels").

    Attributes:
        video_id: A unique string ID for the video.
        video_url: URL of the video.
        thumbnail_url: URL of the video's thumbnail.
        title: Title of the video.
        length: Length of the video.
        channel: Name of the channel that uploaded the video.
        channel_url: URL of the uploader's channel.
        channel_thumbnail_url: URL of the avatar of the uploader's channel.
        uploaded_on: A string specifying when the video was uploaded.
        view_count_text: A string with the number of views for the video.
    """
    video_id: str
    video_url: str
    thumbnail_url: str
    title: str
    length: str
    channel: str
    channel_url: str
    channel_thumbnail_url: str
    uploaded_on: str
    view_count_text: str

    def __str__(self):
        return f"""[{self.video_id}] {self.title} ({self.length}) - {self.view_count_text}
by: {self.channel} - uploaded {self.uploaded_on} - {self.video_url}
"""