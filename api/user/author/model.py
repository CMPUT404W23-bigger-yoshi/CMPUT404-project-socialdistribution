from dataclasses import asdict, dataclass

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import event

from api import db
from api.user.relations import author_likes_comments, author_likes_posts
from api.utils import generate_object_ID


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
    username: str = db.Column("username", db.String(20), nullable=False, unique=True)
    password: str = db.Column("password", db.String(64), nullable=False)
    github: str = db.Column("github", db.Text, nullable=True)
    profile_image: str = db.Column("profile_image", db.Text, default="")

    def getJSON(self) -> dict:
        json = asdict(self)
        json["type"] = "author"
        json["id"] = json["url"]
        del json["password"]
        return json
