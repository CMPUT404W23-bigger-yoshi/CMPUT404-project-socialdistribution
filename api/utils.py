from dataclasses import dataclass

from flask import request


@dataclass
class Paginator:
    size: int
    page: int


def get_pagination_params() -> Paginator:
    return Paginator(page=request.args.get("page", 1, type=int), size=request.args.get("size", 10, type=int))
