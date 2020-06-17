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
                [(p.absolute_uri, int(p.stream_info.bandwidth)) for p in self.playlist.playlists],
                key=lambda bu: -bu[1]
            )
            log.info(f"Multi playlists found, loading the video which bandwidth={bw_uri[0][1]} uri={bw_uri[0][0]}")
            self.playlist = m3u8.load(bw_uri[0][0])
        if len(self.playlist.keys) > 0:
            key = http_get(self.playlist.keys[0].absolute_uri)
            cryptor = AES.new(key, AES.MODE_CBC)
            self.crypto_func = lambda data: cryptor.decrypt(data)
            log.info(f"Key found, AES{key}")
        else:
            self.crypto_func = lambda x: x

    def download(self, target: str):
        with open(target, "wb") as fp:
            for seg in self.playlist.segments:
                fp.write(self.crypto_func(http_get(seg.absolute_uri)))
