import enum
import logging
import random
import re
import uuid
from dataclasses import asdict, dataclass

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
    PRIVATE = 2


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


def get_object_type(object_uri: str) -> str:
    """
    Returns the object type in string format based
    on the id.
    """
    comment_pattern = ".*/authors/.*/posts/.*/comments.*"
    post_pattern = ".*/authors/.*/posts.*"
    auth_pattern = ".*/authors.*"

    if re.match(comment_pattern, object_uri):
        return "comment"
    elif re.match(post_pattern, object_uri):
        return "post"
    elif re.match(auth_pattern, object_uri):
        return "author"
    else:
        raise ValueError("unknown pattern")


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
    return str(uuid.uuid4())
