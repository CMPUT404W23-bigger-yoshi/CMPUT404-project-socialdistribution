from dataclasses import dataclass
import enum
from flask import request
import hashlib
import os
import time

increment = 0


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


@dataclass
class Paginator:
    size: int
    page: int


def get_pagination_params() -> Paginator:
    return Paginator(page=request.args.get("page", 1, type=int), size=request.args.get("size", 10, type=int))

def generate_object_ID() -> str:
    global increment
    pid = "%08x" % os.getpid()
    ti = "%08x" % int(time.time())
    num = "%08x" % increment
    increment += 1
    return ti + num + pid




