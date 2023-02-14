from dataclasses import dataclass
import enum
from sqlalchemy import Enum
from flask import request


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


@dataclass
class Paginator:
    size: int
    page: int


def get_pagination_params() -> Paginator:
    return Paginator(
        page=request.args.get("page") if request.args.get("page", "").isdigit() else 1,
        size=request.args.get("size") if request.args.get("size", "").isdigit() else 10,
    )
