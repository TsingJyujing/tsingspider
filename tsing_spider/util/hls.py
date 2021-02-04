import logging
from typing import Iterable, Tuple

import m3u8
from Cryptodome.Cipher import AES
from m3u8 import Segment

from .pyurllib import http_get

log = logging.getLogger(__file__)


class M3U8Downloader:
    def __init__(self, index_url: str, headers: dict = None, retry_count: int = 5):
        self.retry_count = retry_count
        self.playlist = m3u8.load(index_url)
        self.headers = headers
        if len(self.playlist.playlists) > 0:
            bw_uri = sorted(
                [
                    (
                        p.absolute_uri,
                        int(p.stream_info.bandwidth)
                    )
                    for p in self.playlist.playlists
                ],
                key=lambda bu: -bu[1]
            )
            log.info(f"Multi playlists found, loading the video which bandwidth={bw_uri[0][1]} uri={bw_uri[0][0]}")
            self.playlist = m3u8.load(bw_uri[0][0])
        playlist_keys = [x for x in self.playlist.keys if x is not None]
        if len(playlist_keys) == 1:
            key = self.playlist.keys[0]
            if not key.method.startswith("AES"):
                raise Exception(f"Unsupported crypt method: {key.method}")
            else:
                log.info(f"Key found, method={key.method}")
            _aes = AES.new(http_get(key.absolute_uri), AES.MODE_CBC)
            self._decrypt_func = lambda data: _aes.decrypt(data)
        elif len(playlist_keys) == 0:
            log.info("No keys found in index file.")
            self._decrypt_func = lambda data: data
        else:
            raise Exception(f"Too much ({len(playlist_keys)}) keys found.")

    def data_stream(self):
        yield from (data for _, data in self.segment_data_generator())

    def segment_data_generator(self) -> Iterable[Tuple[Segment, bytes]]:
        total = len(self.playlist.segments)
        for i, seg in enumerate(self.playlist.segments):
            log.debug(f"Downloading {i + 1}/{total} segment: {seg.absolute_uri}")
            data = None
            ex = None
            for j in range(self.retry_count):
                # noinspection PyBroadException
                try:
                    data = self._decrypt_func(http_get(seg.absolute_uri, headers=self.headers))
                except Exception as ex:
                    log.debug(f"Failed while downloading segment {i + 1}/{total} retry {j + 1}/{self.retry_count}")
            if data is None:
                if ex is not None:
                    raise ex
                else:
                    raise ValueError(f"Downloaded data segment {i + 1}/{total} is empty.")
            else:
                yield seg, data

    def download_to(self, target: str):
        """
        Download ts file to one file
        @param target:
        @return:
        """
        with open(target, "wb") as fp:
            for ds in self.data_stream():
                fp.write(ds)
