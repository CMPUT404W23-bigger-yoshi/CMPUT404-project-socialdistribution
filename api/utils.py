from dataclasses import dataclass

from flask import request


@dataclass
class Paginator:
    size: int
    page: int


def get_pagination_params() -> Paginator:
    return Paginator(
        page=request.args.get("page") if request.args.get("page", "").isdigit() else 1,
        size=request.args.get("size") if request.args.get("size", "").isdigit() else 10,
    )
