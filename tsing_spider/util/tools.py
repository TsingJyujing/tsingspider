from datetime import datetime
from html import unescape


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
