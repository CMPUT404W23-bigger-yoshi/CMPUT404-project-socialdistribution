import enum
from datetime import datetime

from sqlalchemy import Enum

from api.app import db


class Visibility(enum.Enum):
    PUBLIC = 0
    FRIENDS = 1


class Post(db.Model):
    _id = db.Column(db.Integer, primary_key=True)
    _published = db.Column("published", db.DateTime, nullable=False)
    _title = db.Column("title", db.String(120), nullable=False)
    _origin = db.Column("origin", db.Text, nullable=False)
    _source = db.Column("source", db.Text, nullable=False)
    _description = db.Column("short_desc", db.String(100))
    _contentType = db.Column("contentType", db.String(50), nullable=False)
    _content = db.Column("content", db.Text, nullable=False)

    # categories will be comma separated values
    _categories = db.Column("categories", db.Text)

    # 0 -> "PUBLIC", 1-> "FRIENDS"
    _visibility = db.Column("visibility", Enum(Visibility), nullable=False)

    _unlisted = db.Column("unlisted", db.Boolean, nullable=False)

    # Foreign Key
    _auth_id = db.Column("auth_id", db.Integer, db.ForeignKey("author.id"), nullable=False)

    # Relationships
    _comments = db.relationship("Comment", backref="post", lazy="dynamic")

    def __init__(
        self,
        title: str,
        auth_id: int,
        published: datetime,
        origin: str,
        source: str,
        contentType: str,
        content: str,
        categories: str,
        visibility="PUBLIC",
        unlisted="False",
        description="",
    ):
        self._title = title
        self._auth_id = auth_id
        self._published = published
        self._origin = origin
        self._source = source
        self._contentType = contentType
        self._content = content
        self._categories = categories
        self._visibility = visibility
        self._unlisted = unlisted
        self._description = description

    def __repr__(self) -> str:
        repr = (
            ""
            + "<< Post: {}\n"
            + "   Title: {}\n"
            + "   Author-id: {}\n"
            + "   Description: {}\n"
            + "   Published on: {}\n"
            + "   Content-Type: {}\n"
            + "   Content: {}\n"
            + "   Origin: {}\n"
            + "   Source: {}\n"
            + "   Categories: {}\n"
            + "   Visibility: {}\n"
            + "   Unlisted: {}>>\n"
        ).format(
            self._id,
            self._title,
            self._auth_id,
            self._description,
            self._published,
            self._contentType,
            self._content,
            self._origin,
            self._source,
            self._categories,
            self._visibility,
            self._unlisted,
        )

        return repr
