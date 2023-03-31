from dataclasses import asdict, dataclass
from datetime import datetime

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Enum, event
from sqlalchemy.ext.hybrid import hybrid_property

from api import db
from api.admin.APIConfig import APIConfig
from api.user.followers.model import LocalFollower
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import Approval, Role, generate_object_ID, randomized_profile_img


def _constructURL(context):
    host = "https://bigger-yoshi.herokuapp.com/"
    authorId = context.get_current_parameters()["id"]
    return host + "authors/" + authorId


def _default_approval_from_config(context):
    if APIConfig.AUTHOR_AUTO_APPROVE:
        return Approval.APPROVED
    else:
        return Approval.PENDING


@dataclass
class Author(UserMixin, db.Model):
    id: str = db.Column(db.Text, primary_key=True, default=generate_object_ID)
    url: str = db.Column("url", db.Text, nullable=True, unique=True, default=_constructURL)
    host: str = db.Column("host", db.Text, nullable=False)
    username: str = db.Column("username", db.Text, nullable=False, unique=True)
    password: str = db.Column("password", db.Text, nullable=False)
    github: str = db.Column("github", db.Text, nullable=True)
    profile_image: str = db.Column("profile_image", db.Text, default=randomized_profile_img)
    approval: Approval = db.Column("approval", Enum(Approval), nullable=False, default=_default_approval_from_config)
    role: Role = db.Column("role", Enum(Role), nullable=False, default=Role.USER)

    @hybrid_property
    def is_approved(self):
        return self.approval == Approval.APPROVED

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
        del json["role"]
        return json


# we use this table to cache non-local authors
@dataclass
class NonLocalAuthor(db.Model):
    id: str = db.Column(db.Text, primary_key=True, unique=True)
    url: str = db.Column("url", db.Text, nullable=True, unique=True)
    host: str = db.Column("host", db.Text, nullable=False)
    displayName: str = db.Column("displayName", db.Text, nullable=False, unique=True)
    github: str = db.Column("github", db.Text, nullable=False)
    profileImage: str = db.Column("profileImage", db.Text, nullable=False)

    def getJSON(self):
        json = asdict(self)
        json["type"] = "author"
        return json
