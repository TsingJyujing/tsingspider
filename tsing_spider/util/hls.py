import logging

import m3u8
from Cryptodome.Cipher import AES

from .pyurllib import http_get

log = logging.getLogger(__file__)


class M3U8Downloader:
    def __init__(self, index_url: str):
        self.playlist = m3u8.load(index_url)
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
        if len(self.playlist.keys) == 1 and self.playlist.keys[0] is not None:
            key = self.playlist.keys[0]
            if not key.method.startswith("AES"):
                raise Exception(f"Unsupported crypt method: {key.method}")
            else:
                log.info(f"Key found, method={key.method}")
            _aes = AES.new(http_get(key.absolute_uri), AES.MODE_CBC)
            self._crypto_func = lambda data: _aes.decrypt(data)
        elif len(self.playlist.keys) == 0:
            log.info("No keys found in index file.")
            self._crypto_func = lambda data: data
        else:
            raise Exception(f"Too much ({len(self.playlist.keys)}) keys found.")

    def data_stream(self):
        yield from (
            self._crypto_func(http_get(seg.absolute_uri))
            for seg in self.playlist.segments
        )

    def download_to(self, target: str):
        with open(target, "wb") as fp:
            for ds in self.data_stream():
                fp.write(ds)
