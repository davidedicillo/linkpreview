import time
import requests

from .exceptions import (
    InvalidContentError,
    InvalidMimeTypeError,
    MaximumContentSizeError,
)


class LinkGrabber:
    def __init__(
        self,
        initial_timeout: int = 20,
        maxsize: int = 1048576,
        receive_timeout: int = 10,
        chunk_size: int = 1024,
    ):
        """
        :param initial_timeout in seconds
        :param maxsize in bytes (default 1048576 = 1 MB)
        :param receive_timeout in seconds
        :param chunk_size in bytes
        """
        self.initial_timeout = initial_timeout
        self.maxsize = maxsize
        self.receive_timeout = receive_timeout
        self.chunk_size = chunk_size

    def get_content(self, url: str):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
            'From': 'info@listlink.co'  # This is another valid field
        }
        r = requests.get(
            url, stream=True, timeout=self.initial_timeout, headers=headers
        )
        r.raise_for_status()

        content_type = r.headers.get("content-type")
        if not content_type:
            print("Invalid content type")
            raise InvalidContentError("Invalid content type")

        mime_type = content_type.split(";")[0].lower()
        if mime_type != "text/html":
            print("Invalid mime type")
            raise InvalidMimeTypeError("Invalid mime type")

        length = r.headers.get("Content-Length")
        if length and int(length) > self.maxsize:
            print("response too large")
            raise MaximumContentSizeError("response too large")

        size = 0
        start = time.time()
        content = b""
        for chunk in r.iter_content(self.chunk_size):
            if time.time() - start > self.receive_timeout:
                print("timeout reached")
                raise TimeoutError("timeout reached")

            size += len(chunk)
            if size > self.maxsize:
                print("response too large")
                raise MaximumContentSizeError("response too large")

            content += chunk

        return content
