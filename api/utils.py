from dataclasses import asdict, dataclass

from flask import request
from werkzeug.security import generate_password_hash


def password_hash(password: str):
    return generate_password_hash(password, method="sha256")


@dataclass
class Paginator:
    # property names chose to match SQLA's API
    per_page: int
    page: int

    @property
    def as_dict(self):
        """returns a dictionary"""
        return asdict(self)


def get_pagination_params() -> Paginator:
    return Paginator(page=request.args.get("page", 1, type=int), per_page=request.args.get("per_page", 10, type=int))
