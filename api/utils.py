import enum
import os
import random
import time
from dataclasses import dataclass

from flask import request

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
    pid = "%04x" % (os.getpid() % ((2**15) - 1))
    ti = "%08x" % int(time.time())
    num = "%04x" % int(increment % ((2**15) - 1))
    ran = "%04x" % int(random.random() * 10e6)
    increment += 1
    return ti + num + ran + pid
