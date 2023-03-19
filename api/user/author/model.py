from dataclasses import asdict, dataclass
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, event

from api import db
from api.user.followers.model import follows_table
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Approval, generate_object_ID, randomized_profile_img


def _constructURL(context):
    host = context.get_current_parameters()["host"]
    id = context.get_current_parameters()["id"]
    host = host + "/" if not host.endswith("/") else host
    return host + "authors/" + id


@dataclass
class Author(UserMixin, db.Model):
    id: str = db.Column(db.String(50), primary_key=True, default=generate_object_ID)
    url: str = db.Column("url", db.Text, nullable=True, unique=False, default=_constructURL)
    host: str = db.Column("host", db.Text, nullable=False)
    username: str = db.Column("username", db.Text, nullable=False, unique=True)
    password: str = db.Column("password", db.Text, nullable=False)
    github: str = db.Column("github", db.Text, nullable=True)
    profile_image: str = db.Column("profile_image", db.Text, default=randomized_profile_img)
    approval: Approval = db.Column("approval", Enum(Approval), nullable=False, default=Approval.APPROVED)

    follows = db.relationship(
        "Author",
        secondary=follows_table,
        primaryjoin=id == follows_table.c.followed_id,
        secondaryjoin=id == follows_table.c.follower_id,
        lazy="dynamic",
    )  # only load followers when requested
    non_local_follows = db.relationship("NonLocalFollower", lazy="dynamic")

    def getJSON(self) -> dict:
        json = asdict(self)
        json["type"] = "author"
        json["id"] = json["url"]
        json["profileImage"] = json["profile_image"]
        json["displayName"] = json["username"]

        del json["username"]
        del json["profile_image"]
        del json["password"]
        del json["approval"]
        return json
