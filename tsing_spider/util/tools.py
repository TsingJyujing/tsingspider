import base64
import hashlib
from datetime import datetime
from html import unescape

import bencodepy


def create_magnet_uri(data: bytes):
    # noinspection PyTypeChecker
    metadata: dict = bencodepy.decode(data)
    subj = metadata[b'info']
    hashcontents = bencodepy.encode(subj)
    digest = hashlib.sha1(hashcontents).digest()
    b32hash = base64.b32encode(digest).decode()
    magnet_uri = 'magnet:?' + 'xt=urn:btih:' + b32hash
    if b"announce" in metadata:
        magnet_uri += ('&tr=' + metadata[b'announce'].decode())
    if b"info" in metadata:
        metadata_info = metadata[b'info']
        if b"name" in metadata_info:
            magnet_uri += ('&dn=' + metadata[b'info'][b'name'].decode())
        if b"length" in metadata_info:
            magnet_uri += ('&xl=' + str(metadata[b'info'][b'length']))
    return magnet_uri


def process_html_string(text: str):
    """
    Process the text content in HTML DOM
    :param text:
    :return:
    """
    return unescape(text.strip(" \n\r"))


def priority_get_from_dict(d: dict, ks: list):
    """
    For each element k in ks, trying to find k as a key in d, if found, then return the value
    :param d:
    :param ks:
    :return:
    """
    for k in ks:
        if k in d:
            return d[k]
    raise Exception("Can't find key in dict: {} not contains in {}".format(",".join(ks), ",".join(d.keys())))


def time_parser(datestr: str):
    return datetime.strptime(datestr, "%Y-%m-%d %H:%M:%S")


def try_to_json(jsonable_object):
    return jsonable_object.json if jsonable_object is not None else None
