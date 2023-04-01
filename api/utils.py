import enum
import json
import logging
import random
import re
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from string import ascii_lowercase
from typing import Any, Dict, Tuple

import requests
from flask import request

logger = logging.getLogger(__name__)

PROFILE_IMG_CHOICES = [
    "https://play.nintendo.com/images/profile-mk-yoshi.babe07bc.7fdea5d658b63e27.png",
    "https://www.lego.com/cdn/cs/catalog/assets/blt7ddbdd57883028de/1/Yoshi_Portrait_CH_Asset.png",
    "https://www.giantbomb.com/a/uploads/scale_small/9/95666/1910416-yoshi_mario_s_hat_super_mario__64.png",
]


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


class Approval(enum.Enum):
    APPROVED = "APPROVED"
    PENDING = "PENDING"


class Role(enum.Enum):
    ADMIN = "ADMIN"
    USER = "USER"


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
    return Paginator(page=request.args.get("page", 1, type=int), per_page=request.args.get("size", 10, type=int))


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
        return ""


def is_admin_endpoint(path):
    pattern = "/admin.*"
    return True if re.match(pattern, path) else False


def get_author_info(url):
    # TODO this is error prone. Should we really do this
    try:
        response = requests.get(url)
        if response.status_code != 200:
            raise
        # Does this need to be JSON??
        return response.content
    except requests.exceptions.ConnectionError:
        # We need to include in API spec that we didnt find info
        # of the author so we are sending minimal info (all we have)
        return {"id": url, "url": url}
    except Exception:
        return None


def randomized_profile_img():
    return random.choice(PROFILE_IMG_CHOICES)


def generate_object_ID() -> str:
    return "".join(map(str, random.choices(ascii_lowercase + "".join(map(str, range(10))), k=16)))


@dataclass
class CachedResponse:
    time: datetime
    resp: Any


class _RequestCacher:
    """
    requests doesn't cache responses, let's roll our own
    ignore cache control headers
    embrace client knowing what's best for it
    (in reality, lots of endpoints don't have cache control implemented, and we hammer endpoints)
    """

    def __init__(self, cache_time_s: float):
        self.responses: Dict[Tuple, CachedResponse] = {}
        self.cache_timedelta = timedelta(seconds=cache_time_s)

    def _retrieve_from_cache_or_make_request(self, key):
        refresh = True
        if key in self.responses.keys():
            cached_resp = self.responses[key]
            # if now is past the amount of time we intended to cache for...
            if datetime.now() < (cached_resp.time + self.cache_timedelta):
                # no need to re-make the request, it's within the caching interval
                refresh = False

        if refresh:
            # wow this is really uglier than i intended it to be. too late to go back idc
            cached_resp = self.responses[key] = CachedResponse(datetime.now(), key[0](*key[1], **json.loads(key[2])))

        return cached_resp.resp

    def get(self, *args, **kwargs):
        # ok, I'm sorry. I never realized that this way of implementing caching would have been so cursed
        # I never would have done it
        key = (requests.get, tuple(args), json.dumps(kwargs, sort_keys=True))
        return self._retrieve_from_cache_or_make_request(key)


cache_request = _RequestCacher(cache_time_s=10)
