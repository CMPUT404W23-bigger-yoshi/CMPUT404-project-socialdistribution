import enum
import os
import random
import re
import time
from dataclasses import asdict, dataclass

from flask import request

increment = 0


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


@dataclass
class Paginator:
    # property names chose to match SQLA's API
    per_page: int
    page: int

    @property
    def dict(self):
        """returns a dictionary"""
        return asdict(self)


def get_pagination_params() -> Paginator:
    return Paginator(page=request.args.get("page", 1, type=int), size=request.args.get("size", 10, type=int))


def get_object_type(ID) -> str:
    """
    Returns the object type in string format based
    on the id.
    """
    comment_pattern = ".*/authors/.*/posts/.*/comments.*"
    post_pattern = ".*/authors/.*/posts.*"
    auth_pattern = ".*/authors.*"

    if re.match(comment_pattern, ID):
        return "comment"
    elif re.match(post_pattern, ID):
        return "post"
    elif re.match(auth_pattern, ID):
        return "author"
    else:
        return None


def get_author_info(url):
    # TODO this is error prone. Should we really do this
    try:
        return requests.get(url).content
    except requests.exceptions.ConnectionError:
        return {"id": url, "url": url}


def generate_object_ID() -> str:
    global increment
    pid = "%04x" % (os.getpid() % ((2**15) - 1))
    ti = "%08x" % int(time.time())
    num = "%04x" % int(increment % ((2**15) - 1))
    ran = "%04x" % int(random.random() * 10e6)
    increment += 1
    return ti + num + ran + pid
